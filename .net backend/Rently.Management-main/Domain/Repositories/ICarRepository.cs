using Rently.Management.Domain.Entities;

namespace Rently.Management.Domain.Repositories;

public interface ICarRepository
{
    Task<Car?> GetByIdAsync(int id);
    Task<PagedResult<Car>> GetCarsAsync(string? search, string? status, int page, int pageSize);
    Task<CarStatistics> GetStatisticsAsync();
    Task<Car> CreateAsync(Car car);
    Task<Car> UpdateAsync(Car car);
    Task DeleteAsync(Car car);
    Task<bool> ExistsAsync(int id);
}

public class CarStatistics
{
    public int TotalCars { get; set; }
    public double TotalCarsChangePercent { get; set; }
    public int Available { get; set; }
    public int OnTrip { get; set; }
    public int Pending { get; set; }
    public int Offline { get; set; }
}
