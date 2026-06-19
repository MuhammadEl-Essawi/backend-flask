using Microsoft.EntityFrameworkCore;
using Rently.Management.Domain.Entities;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi;

namespace Rently.Management.Infrastructure.Repositories;

public class CarRepository : ICarRepository
{
    private readonly ApplicationDbContext _context;

    public CarRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Car?> GetByIdAsync(int id)
    {
        return await _context.Cars
            .Include(c => c.Owner)
            .Include(c => c.Images)
            .FirstOrDefaultAsync(c => c.Id == id);
    }

    public async Task<PagedResult<Car>> GetCarsAsync(string? search, string? status, int page, int pageSize)
    {
        var query = _context.Cars
            .Include(c => c.Owner)
            .Include(c => c.Images)
            .AsQueryable();

        // Search by license plate
        if (!string.IsNullOrEmpty(search))
        {
            query = query.Where(c => 
                c.LicensePlate != null && c.LicensePlate.Contains(search));
        }

        // Filter by status
        if (!string.IsNullOrEmpty(status) && status != "All")
        {
            query = query.Where(c => c.Status == status);
        }

        var totalCount = await query.CountAsync();

        var cars = await query
            .OrderByDescending(c => c.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        return new PagedResult<Car>
        {
            Data = cars,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)pageSize)
        };
    }

    public async Task<CarStatistics> GetStatisticsAsync()
    {
        var now = DateTime.UtcNow;
        var last30Days = now.AddDays(-30);
        var previous30Days = now.AddDays(-60);

        // Total Cars
        var totalCars = await _context.Cars.CountAsync();
        var totalCarsLast30Days = await _context.Cars
            .CountAsync(c => c.CreatedAt >= last30Days);
        var totalCarsPrevious30Days = await _context.Cars
            .CountAsync(c => c.CreatedAt >= previous30Days && c.CreatedAt < last30Days);
        var totalCarsChangePercent = totalCarsPrevious30Days > 0
            ? ((double)(totalCarsLast30Days - totalCarsPrevious30Days) / totalCarsPrevious30Days) * 100
            : (totalCarsLast30Days > 0 ? 100 : 0);

        // Available (Status = "Available")
        var available = await _context.Cars
            .CountAsync(c => c.Status == "Available");

        // On Trip (Status = "On Trip" or "Rented")
        var onTrip = await _context.Cars
            .CountAsync(c => c.Status == "On Trip" || c.Status == "Rented");

        // Pending (Status = "Pending")
        var pending = await _context.Cars
            .CountAsync(c => c.Status == "Pending");

        // Offline (Status = "Offline" or "Maintenance")
        var offline = await _context.Cars
            .CountAsync(c => c.Status == "Offline" || c.Status == "Maintenance");

        return new CarStatistics
        {
            TotalCars = totalCars,
            TotalCarsChangePercent = Math.Round(totalCarsChangePercent, 1),
            Available = available,
            OnTrip = onTrip,
            Pending = pending,
            Offline = offline
        };
    }

    public async Task<Car> CreateAsync(Car car)
    {
        car.CreatedAt = DateTime.UtcNow;
        _context.Cars.Add(car);
        await _context.SaveChangesAsync();
        return car;
    }

    public async Task<Car> UpdateAsync(Car car)
    {
        car.UpdatedAt = DateTime.UtcNow;
        _context.Cars.Update(car);
        await _context.SaveChangesAsync();
        return car;
    }

    public async Task DeleteAsync(Car car)
    {
        _context.Cars.Remove(car);
        await _context.SaveChangesAsync();
    }

    public async Task<bool> ExistsAsync(int id)
    {
        return await _context.Cars.AnyAsync(c => c.Id == id);
    }
}
