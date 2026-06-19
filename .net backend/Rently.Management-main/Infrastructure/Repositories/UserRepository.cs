using Microsoft.EntityFrameworkCore;
using Rently.Management.Domain.Entities;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi;

namespace Rently.Management.Infrastructure.Repositories;

public class UserRepository : IUserRepository
{
    private readonly ApplicationDbContext _context;

    public UserRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<User?> GetByIdAsync(int id)
    {
        return await _context.Users.FindAsync(id);
    }

    public async Task<User?> GetByEmailAsync(string email)
    {
        var e = (email ?? "").Trim().ToLowerInvariant();
        return await _context.Users
            .FirstOrDefaultAsync(u => (u.Email ?? "").ToLower() == e);
    }

    public async Task<PagedResult<User>> GetUsersAsync(string? search, string? status, int page, int pageSize)
    {
        var query = _context.Users.AsQueryable();

        // Search by name or email
        if (!string.IsNullOrEmpty(search))
        {
            query = query.Where(u => 
                (u.FirstName != null && u.FirstName.Contains(search)) ||
                (u.LastName != null && u.LastName.Contains(search)) ||
                (u.Email != null && u.Email.Contains(search)));
        }

        // Filter by status (ApprovalStatus)
        if (!string.IsNullOrEmpty(status) && status != "All")
        {
            var approvalStatus = GetApprovalStatusFromStatus(status);
            query = query.Where(u => u.ApprovalStatus == approvalStatus);
        }

        var totalCount = await query.CountAsync();

        var users = await query
            .OrderByDescending(u => u.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        return new PagedResult<User>
        {
            Data = users,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)pageSize)
        };
    }

    public async Task<PagedResult<User>> GetActivationRequestsAsync(int page, int pageSize)
    {
        var query = _context.Users
            .Where(u => u.ApprovalStatus == "Pending");

        var totalCount = await query.CountAsync();

        var users = await query
            .OrderByDescending(u => u.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        return new PagedResult<User>
        {
            Data = users,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)pageSize)
        };
    }

    public async Task<User> CreateAsync(User user)
    {
        user.CreatedAt = DateTime.UtcNow;
        _context.Users.Add(user);
        await _context.SaveChangesAsync();
        return user;
    }

    public async Task<User> UpdateAsync(User user)
    {
        user.UpdatedAt = DateTime.UtcNow;
        _context.Users.Update(user);
        await _context.SaveChangesAsync();
        return user;
    }

    public async Task DeleteAsync(User user)
    {
        _context.Users.Remove(user);
        await _context.SaveChangesAsync();
    }

    public async Task<bool> ExistsAsync(int id)
    {
        return await _context.Users.AnyAsync(u => u.Id == id);
    }

    private string GetApprovalStatusFromStatus(string status)
    {
        return status switch
        {
            "Active" => "Approved",
            "Blocked" => "Rejected",
            "Non-Active" => "Pending",
            _ => "Pending"
        };
    }
}
