using Rently.Management.Domain.Common;

namespace Rently.Management.Domain.Entities;

public class Review : AuditableEntity
{
    public int Id { get; set; }

    public int RenterId { get; set; }
    public int CarId { get; set; }

    public int Rating { get; set; }                 // 1–5
    public string? Comment { get; set; }

    public User? Renter { get; set; }
    public Car? Car { get; set; }
}