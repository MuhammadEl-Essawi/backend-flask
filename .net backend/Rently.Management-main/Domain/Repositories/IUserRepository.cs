using Rently.Management.Domain.Entities;

namespace Rently.Management.Domain.Repositories;

public interface IUserRepository
{
    Task<User?> GetByIdAsync(int id);
    Task<User?> GetByEmailAsync(string email);
    Task<PagedResult<User>> GetUsersAsync(string? search, string? status, int page, int pageSize);
    Task<PagedResult<User>> GetActivationRequestsAsync(int page, int pageSize);
    Task<User> CreateAsync(User user);
    Task<User> UpdateAsync(User user);
    Task DeleteAsync(User user);
    Task<bool> ExistsAsync(int id);
}

public class PagedResult<T>
{
    public List<T> Data { get; set; } = new();
    public int TotalCount { get; set; }
    public int Page { get; set; }
    public int PageSize { get; set; }
    public int TotalPages { get; set; }
}
