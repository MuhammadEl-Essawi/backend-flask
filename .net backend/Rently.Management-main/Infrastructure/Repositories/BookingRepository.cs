using Microsoft.EntityFrameworkCore;
using Rently.Management.Domain.Entities;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi;

namespace Rently.Management.Infrastructure.Repositories;

public class BookingRepository : IBookingRepository
{
    private readonly ApplicationDbContext _context;

    public BookingRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Booking?> GetByIdAsync(int id)
    {
        return await _context.Bookings
            .Include(b => b.Car)
                .ThenInclude(c => c!.Owner)
            .Include(b => b.Car)
                .ThenInclude(c => c!.Images)
            .Include(b => b.Renter)
            .Include(b => b.Payments)
            .FirstOrDefaultAsync(b => b.Id == id);
    }

    public async Task<PagedResult<Booking>> GetBookingsAsync(string? search, string? status, int page, int pageSize)
    {
        var query = _context.Bookings
            .Include(b => b.Car)
                .ThenInclude(c => c!.Owner)
            .Include(b => b.Car)
                .ThenInclude(c => c!.Images)
            .Include(b => b.Renter)
            .AsQueryable();

        // Search by TransactionId or Booking Id
        if (!string.IsNullOrWhiteSpace(search))
        {
            search = search.Trim();

            if (int.TryParse(search, out var bookingId))
            {
                query = query.Where(b => b.Id == bookingId);
            }
            else
            {
                query = query.Where(b =>
                    (b.TransactionId != null && b.TransactionId.Contains(search)) ||
                    b.Id.ToString().Contains(search));
            }
        }

        // Filter by UI status
        if (!string.IsNullOrWhiteSpace(status) && status != "All")
        {
            var today = DateTime.UtcNow.Date;
            var normalized = NormalizeUiStatus(status);

            query = normalized switch
            {
                "Canceled" => query.Where(b => b.Status == "Cancelled" || b.Status == "Canceled"),
                "Pending" => query.Where(b => b.Status == "Pending"),
                "Completed" => query.Where(b => b.Status == "Completed" || b.EndDate.Date < today),
                "Up coming" => query.Where(b =>
                    (b.Status == "Confirmed" || b.Status == "Active") &&
                    b.StartDate.Date > today),
                "Active" => query.Where(b =>
                    (b.Status == "Confirmed" || b.Status == "Active") &&
                    b.StartDate.Date <= today &&
                    b.EndDate.Date >= today),
                _ => query
            };
        }

        var totalCount = await query.CountAsync();

        var bookings = await query
            .OrderByDescending(b => b.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        return new PagedResult<Booking>
        {
            Data = bookings,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)pageSize)
        };
    }

    public async Task<BookingStatistics> GetStatisticsAsync(DateTime? today = null)
    {
        var date = (today ?? DateTime.UtcNow).Date;

        var activeTrips = await _context.Bookings.CountAsync(b =>
            (b.Status == "Confirmed" || b.Status == "Active") &&
            b.StartDate.Date <= date &&
            b.EndDate.Date >= date);

        var pickUpToday = await _context.Bookings.CountAsync(b =>
            b.StartDate.Date == date &&
            b.Status != "Cancelled" && b.Status != "Canceled");

        var returnToday = await _context.Bookings.CountAsync(b =>
            b.EndDate.Date == date &&
            b.Status != "Cancelled" && b.Status != "Canceled");

        var canceled = await _context.Bookings.CountAsync(b =>
            b.Status == "Cancelled" || b.Status == "Canceled");

        return new BookingStatistics
        {
            ActiveTrips = activeTrips,
            PickUpToday = pickUpToday,
            ReturnToday = returnToday,
            Canceled = canceled
        };
    }

    public async Task<Booking> UpdateAsync(Booking booking)
    {
        booking.UpdatedAt = DateTime.UtcNow;
        _context.Bookings.Update(booking);
        await _context.SaveChangesAsync();
        return booking;
    }

    public async Task<bool> ExistsAsync(int id)
    {
        return await _context.Bookings.AnyAsync(b => b.Id == id);
    }

    public async Task<int> RefundBookingsAsync(List<int> bookingIds, string? reason)
    {
        if (bookingIds.Count == 0) return 0;

        var bookings = await _context.Bookings
            .Include(b => b.Payments)
            .Where(b => bookingIds.Contains(b.Id))
            .ToListAsync();

        foreach (var booking in bookings)
        {
            // Mark booking canceled
            booking.Status = "Cancelled";
            booking.UpdatedAt = DateTime.UtcNow;

            // Create a refund request payment (shown under refunds screen)
            var refund = new Payment
            {
                BookingId = booking.Id,
                UserId = booking.RenterId,
                Amount = booking.PaidAmount > 0 ? booking.PaidAmount : booking.TotalPrice,
                Currency = "EGP",
                Status = "Pending",
                Provider = "Manual",
                FailureMessage = reason
            };

            _context.Payments.Add(refund);
        }

        await _context.SaveChangesAsync();
        return bookings.Count;
    }

    private static string NormalizeUiStatus(string status)
    {
        status = status.Trim();

        if (string.Equals(status, "Upcoming", StringComparison.OrdinalIgnoreCase))
            return "Up coming";

        if (string.Equals(status, "Up coming", StringComparison.OrdinalIgnoreCase))
            return "Up coming";

        if (string.Equals(status, "Cancelled", StringComparison.OrdinalIgnoreCase))
            return "Canceled";

        return status;
    }
}

