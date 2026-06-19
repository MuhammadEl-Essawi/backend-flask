namespace Rently.Management.Domain.Repositories;

public interface IDashboardRepository
{
    Task<DashboardStats> GetStatsAsync();
    Task<List<DailyRevenue>> GetWeeklyRevenueAsync(int days);
    Task<List<MonthlyBooking>> GetBookingsByMonthAsync(int months);
}

public class DashboardStats
{
    public int TotalUsers { get; set; }
    public double UsersChangePercent { get; set; }
    public int TotalCars { get; set; }
    public double CarsChangePercent { get; set; }
    public int TotalBookings { get; set; }
    public double BookingsChangePercent { get; set; }
    public decimal ProfitLast30Days { get; set; }
    public decimal ProfitChangePercent { get; set; }
}

public class DailyRevenue
{
    public DateTime Date { get; set; }
    public decimal Revenue { get; set; }
}

public class MonthlyBooking
{
    public int Year { get; set; }
    public int Month { get; set; }
    public int Count { get; set; }
}
