using Microsoft.EntityFrameworkCore;
using Rently.Management.Domain.Entities;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi;

namespace Rently.Management.Infrastructure.Repositories;

public class PaymentRepository : IPaymentRepository
{
    private readonly ApplicationDbContext _context;

    public PaymentRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Payment?> GetByIdAsync(int id)
    {
        return await _context.Payments
            .Include(p => p.Booking)
                .ThenInclude(b => b!.Car)
                    .ThenInclude(c => c.Owner)
            .Include(p => p.Booking)
                .ThenInclude(b => b!.Renter)
            .Include(p => p.User)
            .FirstOrDefaultAsync(p => p.Id == id);
    }

    public async Task<PagedResult<Payment>> GetTransactionsAsync(string? search, string? type, string? status, int page, int pageSize)
    {
        var query = _context.Payments
            .Include(p => p.Booking)
                .ThenInclude(b => b!.Car)
                    .ThenInclude(c => c.Owner)
            .Include(p => p.Booking)
                .ThenInclude(b => b!.Renter)
            .Include(p => p.User)
            .AsQueryable();

        // Search by TX ID (ProviderPaymentId) or Date
        if (!string.IsNullOrEmpty(search))
        {
            if (DateTime.TryParse(search, out var searchDate))
            {
                query = query.Where(p => p.CreatedAt.Date == searchDate.Date);
            }
            else
            {
                query = query.Where(p => 
                    (p.ProviderPaymentId != null && p.ProviderPaymentId.Contains(search)) ||
                    p.Id.ToString().Contains(search));
            }
        }

        // Filter by type
        if (!string.IsNullOrEmpty(type) && type != "All")
        {
            query = type switch
            {
                "Reservation payment" => query.Where(p => p.Booking != null && p.Status == "Succeeded"),
                "Owner Payout" => query.Where(p => p.Booking != null && p.Booking.Car != null),
                "Refund" => query.Where(p => p.Status == "Refunded" || p.Status == "Refunding"),
                "New booking" => query.Where(p => p.Booking != null && p.CreatedAt >= DateTime.UtcNow.AddDays(-7)),
                _ => query
            };
        }

        // Filter by status
        if (!string.IsNullOrEmpty(status) && status != "All")
        {
            query = query.Where(p => p.Status == status);
        }

        var totalCount = await query.CountAsync();

        var payments = await query
            .OrderByDescending(p => p.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        return new PagedResult<Payment>
        {
            Data = payments,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)pageSize)
        };
    }

    public async Task<PagedResult<Payment>> GetOwnerPayoutsAsync(int page, int pageSize)
    {
        // Owner payouts are payments where the payee is the car owner
        var query = _context.Payments
            .Include(p => p.Booking)
                .ThenInclude(b => b!.Car)
                    .ThenInclude(c => c.Owner)
            .Where(p => p.Booking != null && 
                       p.Booking.Car != null && 
                       p.Status == "Succeeded")
            .AsQueryable();

        var totalCount = await query.CountAsync();

        var payments = await query
            .OrderByDescending(p => p.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        return new PagedResult<Payment>
        {
            Data = payments,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)pageSize)
        };
    }

    public async Task<PagedResult<Payment>> GetRefundsAsync(string? status, int page, int pageSize)
    {
        var query = _context.Payments
            .Include(p => p.Booking)
                .ThenInclude(b => b!.Renter)
            .Where(p => p.Status == "Refunded" || 
                       p.Status == "Refunding" ||
                       p.Status == "Pending" && p.Booking != null)
            .AsQueryable();

        // Filter by refund status
        if (!string.IsNullOrEmpty(status) && status != "All")
        {
            var refundStatus = status switch
            {
                "Under Review" => "Pending",
                "Approved" => "Refunding",
                "Rejected" => "Failed",
                "Completed" => "Refunded",
                _ => status
            };
            query = query.Where(p => p.Status == refundStatus);
        }

        var totalCount = await query.CountAsync();

        var payments = await query
            .OrderByDescending(p => p.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        return new PagedResult<Payment>
        {
            Data = payments,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)pageSize)
        };
    }

    public async Task<PaymentStatistics> GetStatisticsAsync()
    {
        var now = DateTime.UtcNow;
        var last30Days = now.AddDays(-30);
        var previous30Days = now.AddDays(-60);

        // Total Revenue (all succeeded payments)
        var totalRevenue = await _context.Payments
            .Where(p => p.Status == "Succeeded")
            .SumAsync(p => p.Amount);

        var totalRevenueLast30Days = await _context.Payments
            .Where(p => p.Status == "Succeeded" && p.CreatedAt >= last30Days)
            .SumAsync(p => p.Amount);

        var totalRevenuePrevious30Days = await _context.Payments
            .Where(p => p.Status == "Succeeded" && 
                       p.CreatedAt >= previous30Days && 
                       p.CreatedAt < last30Days)
            .SumAsync(p => p.Amount);

        var totalRevenueChangePercent = totalRevenuePrevious30Days > 0
            ? ((double)(totalRevenueLast30Days - totalRevenuePrevious30Days) / (double)totalRevenuePrevious30Days) * 100
            : (totalRevenueLast30Days > 0 ? 100 : 0);

        // Pending Payout (succeeded payments not yet paid to owners)
        var pendingPayout = await _context.Payments
            .Where(p => p.Status == "Succeeded" && 
                       p.Booking != null && 
                       p.Booking.Car != null)
            .SumAsync(p => p.Amount);

        // Profit Last 30 Days (succeeded payments in last 30 days)
        var profitLast30Days = await _context.Payments
            .Where(p => p.Status == "Succeeded" && p.CreatedAt >= last30Days)
            .SumAsync(p => p.Amount);

        var profitPrevious30Days = await _context.Payments
            .Where(p => p.Status == "Succeeded" && 
                       p.CreatedAt >= previous30Days && 
                       p.CreatedAt < last30Days)
            .SumAsync(p => p.Amount);

        var profitChangePercent = profitPrevious30Days > 0
            ? ((double)(profitLast30Days - profitPrevious30Days) / (double)profitPrevious30Days) * 100
            : (profitLast30Days > 0 ? 100 : 0);

        return new PaymentStatistics
        {
            TotalRevenue = totalRevenue,
            TotalRevenueChangePercent = Math.Round(totalRevenueChangePercent, 1),
            PendingPayout = pendingPayout,
            ProfitLast30Days = profitLast30Days,
            ProfitChangePercent = Math.Round(profitChangePercent, 1)
        };
    }

    public async Task<Payment> CreateAsync(Payment payment)
    {
        payment.CreatedAt = DateTime.UtcNow;
        _context.Payments.Add(payment);
        await _context.SaveChangesAsync();
        return payment;
    }

    public async Task<Payment> UpdateAsync(Payment payment)
    {
        payment.UpdatedAt = DateTime.UtcNow;
        _context.Payments.Update(payment);
        await _context.SaveChangesAsync();
        return payment;
    }

    public async Task<bool> ExistsAsync(int id)
    {
        return await _context.Payments.AnyAsync(p => p.Id == id);
    }
}
