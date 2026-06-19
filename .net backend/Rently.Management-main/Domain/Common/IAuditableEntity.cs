// Domain/Common/IAuditableEntity.cs
namespace Rently.Management.Domain.Common;

public interface IAuditableEntity
{
    DateTime CreatedAt { get; set; }
    DateTime? UpdatedAt { get; set; }
    // Optional: add string? CreatedBy, string? UpdatedBy, bool IsDeleted ...
}
