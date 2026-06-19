namespace Rently.Management.Domain.Entities;
using Rently.Management.Domain.Common;


public class Booking : AuditableEntity
{
    public int Id { get; set; }                     // PK

    public int CarId { get; set; }
    public int RenterId { get; set; }

    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }

    public string? Status { get; set; }             // "Pending", "Confirmed", "Completed", "Cancelled"...
    public string? TransactionId { get; set; }
    public decimal TotalPrice { get; set; }             // Total booking price
    public decimal PaidAmount { get; set; }             // Actual amount paid
    public DateTime? PaymentConfirmedAt { get; set; }   // Payment confirmation timestamp
    // Navigation (optional to include in API responses)
    public Car? Car { get; set; }
    public User? Renter { get; set; }
    public List<Payment> Payments { get; set; } = new();
}
