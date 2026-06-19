using Microsoft.EntityFrameworkCore;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi;

namespace Rently.Management.Infrastructure.Repositories;

public class DashboardRepository : IDashboardRepository
{
    private readonly ApplicationDbContext _context;

    public DashboardRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<DashboardStats> GetStatsAsync()
    {
        var now = DateTime.UtcNow;
        var last30Days = now.AddDays(-30);
        var previous30Days = now.AddDays(-60);

        // Total Users
        var totalUsers = await _context.Users.CountAsync();
        var usersLast30Days = await _context.Users
            .CountAsync(u => u.CreatedAt >= last30Days);
        var usersPrevious30Days = await _context.Users
            .CountAsync(u => u.CreatedAt >= previous30Days && u.CreatedAt < last30Days);
        var usersChangePercent = usersPrevious30Days > 0
            ? ((double)(usersLast30Days - usersPrevious30Days) / usersPrevious30Days) * 100
            : (usersLast30Days > 0 ? 100 : 0);

        // Total Cars
        var totalCars = await _context.Cars.CountAsync();
        var carsLast30Days = await _context.Cars
            .CountAsync(c => c.CreatedAt >= last30Days);
        var carsPrevious30Days = await _context.Cars
            .CountAsync(c => c.CreatedAt >= previous30Days && c.CreatedAt < last30Days);
        var carsChangePercent = carsPrevious30Days > 0
            ? ((double)(carsLast30Days - carsPrevious30Days) / carsPrevious30Days) * 100
            : (carsLast30Days > 0 ? 100 : 0);

        // Total Bookings
        var totalBookings = await _context.Bookings.CountAsync();
        var bookingsLast30Days = await _context.Bookings
            .CountAsync(b => b.CreatedAt >= last30Days);
        var bookingsPrevious30Days = await _context.Bookings
            .CountAsync(b => b.CreatedAt >= previous30Days && b.CreatedAt < last30Days);
        var bookingsChangePercent = bookingsPrevious30Days > 0
            ? ((double)(bookingsLast30Days - bookingsPrevious30Days) / bookingsPrevious30Days) * 100
            : (bookingsLast30Days > 0 ? 100 : 0);

        // Profit Last 30 Days
        var profitLast30Days = await _context.Payments
            .Where(p => p.Status == "Succeeded" && p.CreatedAt >= last30Days)
            .SumAsync(p => p.Amount);

        // Profit Previous 30 Days
        var profitPrevious30Days = await _context.Payments
            .Where(p => p.Status == "Succeeded" && 
                       p.CreatedAt >= previous30Days && 
                       p.CreatedAt < last30Days)
            .SumAsync(p => p.Amount);

        var profitChangePercent = profitPrevious30Days > 0
            ? ((profitLast30Days - profitPrevious30Days) / profitPrevious30Days) * 100
            : (profitLast30Days > 0 ? 100 : 0);

        return new DashboardStats
        {
            TotalUsers = totalUsers,
            UsersChangePercent = Math.Round(usersChangePercent, 1),
            TotalCars = totalCars,
            CarsChangePercent = Math.Round(carsChangePercent, 1),
            TotalBookings = totalBookings,
            BookingsChangePercent = Math.Round(bookingsChangePercent, 1),
            ProfitLast30Days = profitLast30Days,
            ProfitChangePercent = Math.Round(profitChangePercent, 1)
        };
    }

    public async Task<List<DailyRevenue>> GetWeeklyRevenueAsync(int days)
    {
        var now = DateTime.UtcNow;
        var startDate = now.AddDays(-days).Date;

        var payments = await _context.Payments
            .Where(p => p.Status == "Succeeded" && p.CreatedAt >= startDate)
            .GroupBy(p => p.CreatedAt.Date)
            .Select(g => new DailyRevenue
            {
                Date = g.Key,
                Revenue = g.Sum(p => p.Amount)
            })
            .ToListAsync();

        // Fill all days (including missing ones with 0)
        var result = new List<DailyRevenue>();
        for (int i = 0; i < days; i++)
        {
            var date = startDate.AddDays(i);
            var existing = payments.FirstOrDefault(p => p.Date.Date == date);
            result.Add(new DailyRevenue
            {
                Date = date,
                Revenue = existing?.Revenue ?? 0
            });
        }

        return result;
    }

    public async Task<List<MonthlyBooking>> GetBookingsByMonthAsync(int months)
    {
        var now = DateTime.UtcNow;
        var startDate = now.AddMonths(-months);

        var bookings = await _context.Bookings
            .Where(b => b.CreatedAt >= startDate)
            .GroupBy(b => new { b.CreatedAt.Year, b.CreatedAt.Month })
            .Select(g => new MonthlyBooking
            {
                Year = g.Key.Year,
                Month = g.Key.Month,
                Count = g.Count()
            })
            .OrderBy(x => x.Year)
            .ThenBy(x => x.Month)
            .ToListAsync();

        return bookings;
    }
}
