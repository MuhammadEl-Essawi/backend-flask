using Rently.Management.Domain.Common;

namespace Rently.Management.Domain.Entities;

public class Car : AuditableEntity
{
    public int Id { get; set; }                     // PK

    public int OwnerId { get; set; }                // FK → User
    public User? Owner { get; set; }                // Navigation (optional in API)

    public string? Brand { get; set; }
    public string? Model { get; set; }
    public int Year { get; set; }
    public decimal PricePerDay { get; set; }
    public string? Status { get; set; }             // "Available", "Rented", "Maintenance" ...
    public string? Transmission { get; set; }       // "Manual", "Automatic"
    public string? Color { get; set; }
    public string? LocationCity { get; set; }
    public decimal AverageRating { get; set; }
    public string? Features { get; set; }           // comma-separated or JSON
    public string? Description { get; set; }
    public string? LicensePlate { get; set; }
    public string? CarLicenseImage { get; set; }

    // Navigation
    public List<Booking> Bookings { get; set; } = new();
    public List<Review> Reviews { get; set; } = new();
    public List<CarImage> Images { get; set; } = new();
    public List<CarUnavailableDate> UnavailableDates { get; set; } = new();
    public List<Favorite> Favorites { get; set; } = new();
}
