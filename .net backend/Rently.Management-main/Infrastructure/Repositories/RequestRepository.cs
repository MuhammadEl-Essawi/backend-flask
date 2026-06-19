using Microsoft.EntityFrameworkCore;
using Rently.Management.Domain.Entities;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi;

namespace Rently.Management.Infrastructure.Repositories;

public class RequestRepository : IRequestRepository
{
    private readonly ApplicationDbContext _context;

    public RequestRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<PagedResult<RequestItem>> GetRequestsAsync(
        string? search,
        string? type,
        string? status,
        string? sort,
        int page,
        int pageSize)
    {
        var ownerRequestsQuery = _context.Users
            .Where(u => u.Role == "Owner")
            .Select(u => new RequestItem
            {
                Id = u.Id,
                Type = "Owner verification",
                SubmittedBy = (u.FirstName + " " + u.LastName).Trim(),
                SubmittedOn = u.CreatedAt,
                TotalPrice = 0,
                Status =
                    u.ApprovalStatus == "Approved"
                        ? "Approved"
                        : (u.ApprovalStatus == "Rejected"
                            ? "Rejected"
                            : "Pending")
            });

        var carListingQuery = _context.Cars
            .Select(c => new RequestItem
            {
                Id = c.Id,
                Type = "Car listing",
                SubmittedBy = (c.Owner != null ? (c.Owner.FirstName + " " + c.Owner.LastName).Trim() : ""),
                SubmittedOn = c.CreatedAt,
                TotalPrice = c.PricePerDay,
                Status =
                    c.Status == "Available"
                        ? "Approved"
                        : (c.Status == "Rejected"
                            ? "Rejected"
                            : "Pending")
            });

        var combined = ownerRequestsQuery.Concat(carListingQuery);

        if (!string.IsNullOrWhiteSpace(search))
        {
            search = search.Trim();
            combined = combined.Where(r =>
                r.Id.ToString().Contains(search) ||
                r.SubmittedBy.Contains(search));
        }

        if (!string.IsNullOrWhiteSpace(type) && type != "All")
        {
            combined = combined.Where(r => r.Type == type);
        }

        if (!string.IsNullOrWhiteSpace(status) && status != "All")
        {
            combined = combined.Where(r => r.Status == status);
        }

        combined = sort switch
        {
            "Newest" => combined.OrderByDescending(r => r.SubmittedOn),
            "Oldest" => combined.OrderBy(r => r.SubmittedOn),
            _ => combined.OrderByDescending(r => r.SubmittedOn)
        };

        var totalCount = await combined.CountAsync();

        var items = await combined
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        return new PagedResult<RequestItem>
        {
            Data = items,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize,
            TotalPages = (int)Math.Ceiling(totalCount / (double)pageSize)
        };
    }

    public async Task<bool> UpdateRequestStatusAsync(int id, string type, string newStatus)
    {
        if (type == "Owner verification")
        {
            var user = await _context.Users.FirstOrDefaultAsync(u => u.Id == id && u.Role == "Owner");
            if (user == null) return false;

            user.ApprovalStatus = newStatus switch
            {
                "Approved" => "Approved",
                "Rejected" => "Rejected",
                "Pending" => "Pending",
                _ => user.ApprovalStatus
            };

            user.UpdatedAt = DateTime.UtcNow;
            await _context.SaveChangesAsync();
            return true;
        }

        if (type == "Car listing")
        {
            var car = await _context.Cars.FirstOrDefaultAsync(c => c.Id == id);
            if (car == null) return false;

            car.Status = newStatus switch
            {
                "Approved" => "Available",
                "Rejected" => "Rejected",
                "Pending" => "Pending",
                _ => car.Status
            };

            car.UpdatedAt = DateTime.UtcNow;
            await _context.SaveChangesAsync();
            return true;
        }

        return false;
    }

    // NOTE: mapping methods removed to keep the entire query server-translatable
}

