using Rently.Management.Domain.Entities;

namespace Rently.Management.Domain.Repositories;

public interface IRequestRepository
{
    Task<PagedResult<RequestItem>> GetRequestsAsync(string? search, string? type, string? status, string? sort, int page, int pageSize);
    Task<bool> UpdateRequestStatusAsync(int id, string type, string newStatus);
}

public class RequestItem
{
    public int Id { get; set; }                      // underlying entity Id
    public string Type { get; set; } = "";           // "Owner verification", "Car listing"
    public string SubmittedBy { get; set; } = "";
    public DateTime SubmittedOn { get; set; }
    public decimal TotalPrice { get; set; }
    public string Status { get; set; } = "";         // "Pending", "Approved", "Rejected"
}

