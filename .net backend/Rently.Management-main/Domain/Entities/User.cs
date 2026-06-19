using Rently.Management.Domain.Common;

namespace Rently.Management.Domain.Entities;

public class User : AuditableEntity
{
    public int Id { get; set; }                     // PK

    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string? Email { get; set; }
    public string? Phone { get; set; }
    public string? Role { get; set; }               // "Owner", "Renter", "Admin" or enum
    public bool IsSuperAdmin { get; set; } = false;
    public string? Nationality { get; set; }
    public string? PreferredLanguage { get; set; }
    public string? LicenseNumber { get; set; }
    public string? ApprovalStatus { get; set; }     // "Pending", "Approved", "Rejected" ...
    public string? PayoutMethod { get; set; }
    public string? PayoutDetails { get; set; }
    public string? BillingCountry { get; set; }
    public string? ZipCode { get; set; }

    public string? PasswordHash { get; set; }
    public string? PasswordSalt { get; set; }
    public string? PasswordResetToken { get; set; }
    public DateTime? PasswordResetTokenExpires { get; set; }

    // Verification images (usually paths or URLs)
    public string? IdImage { get; set; }
    public string? LicenseImage { get; set; }
    public string? PassportImage { get; set; }
    public string? SelfieImage { get; set; }
    public string? ResidenceProofImage { get; set; }
    public string? JobProofImage { get; set; }

    // Navigation properties (relationships)
    public List<Car> OwnedCars { get; set; } = new();
    public List<Booking> BookingsAsRenter { get; set; } = new();
    public List<Review> Reviews { get; set; } = new();
    public List<Notification> Notifications { get; set; } = new();
    public List<Favorite> Favorites { get; set; } = new();
    public List<Message> SentMessages { get; set; } = new();
    public List<Message> ReceivedMessages { get; set; } = new();
    public List<Otp> Otps { get; set; } = new();
    public List<Payment> Payments { get; set; } = new();
}
