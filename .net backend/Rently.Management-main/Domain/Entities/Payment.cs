using Rently.Management.Domain.Common;

namespace Rently.Management.Domain.Entities;

public class Payment : AuditableEntity
{
    public int Id { get; set; }                      // PK

    public int BookingId { get; set; }               // FK → Booking
    public int? UserId { get; set; }                 // Optional: FK → User (payer)

    public decimal Amount { get; set; }              // Required or paid amount
    public string Currency { get; set; } = "SAR";    // Currency, default SAR

    public string Status { get; set; } = "Pending";  // Pending, Succeeded, Failed, Refunded...
    public string? Provider { get; set; }            // Payment gateway (Stripe, Tap, Moyasar…)
    public string? ProviderPaymentId { get; set; }   // Provider-side transaction ID
    public string? ProviderReceiptUrl { get; set; }  // Receipt URL if available

    public string? FailureCode { get; set; }         // Provider error code
    public string? FailureMessage { get; set; }      // Error message

    // Navigation
    public Booking? Booking { get; set; }
    public User? User { get; set; }
}

