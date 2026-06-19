using Rently.Management.Domain.Entities;

namespace Rently.Management.Domain.Repositories;

public interface IBookingRepository
{
    Task<Booking?> GetByIdAsync(int id);
    Task<PagedResult<Booking>> GetBookingsAsync(string? search, string? status, int page, int pageSize);
    Task<BookingStatistics> GetStatisticsAsync(DateTime? today = null);
    Task<Booking> UpdateAsync(Booking booking);
    Task<bool> ExistsAsync(int id);
    Task<int> RefundBookingsAsync(List<int> bookingIds, string? reason);
}

public class BookingStatistics
{
    public int ActiveTrips { get; set; }
    public int PickUpToday { get; set; }
    public int ReturnToday { get; set; }
    public int Canceled { get; set; }
}

