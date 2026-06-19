using System.ComponentModel.DataAnnotations;
namespace Rently.Management.WebApi.DTOs;

public class CarDto
{
    public int Id { get; set; }
    public string CarName { get; set; } = ""; // "Kia Sportage 2019"
    public string PlateNumber { get; set; } = ""; // "1234 | ABC"
    public string OwnerName { get; set; } = ""; // "sheha"
    public decimal PricePerDay { get; set; }
    public string Status { get; set; } = ""; // "Available", "On Trip", "Pending", "Offline"
    public string? ImageUrl { get; set; }
    public int Year { get; set; }
    public string? Brand { get; set; }
    public string? Model { get; set; }
}

public class CreateCarDto
{
    [Required]
    [Range(1, int.MaxValue)]
    public int OwnerId { get; set; }
    [Required]
    public string? Brand { get; set; }
    [Required]
    public string? Model { get; set; }
    [Required]
    [Range(1900, 2100)]
    public int Year { get; set; }
    [Required]
    [Range(typeof(decimal), "0.01", "79228162514264337593543950335")]
    public decimal PricePerDay { get; set; }
    [Required]
    public string? Status { get; set; }
    public string? Transmission { get; set; }
    public string? Color { get; set; }
    public string? LocationCity { get; set; }
    public string? Features { get; set; }
    public string? Description { get; set; }
    [Required]
    public string? LicensePlate { get; set; }
    public string? CarLicenseImage { get; set; }
}

public class UpdateCarDto
{
    public string? Brand { get; set; }
    public string? Model { get; set; }
    public int? Year { get; set; }
    public decimal? PricePerDay { get; set; }
    public string? Status { get; set; }
    public string? Transmission { get; set; }
    public string? Color { get; set; }
    public string? LocationCity { get; set; }
    public string? Features { get; set; }
    public string? Description { get; set; }
    public string? LicensePlate { get; set; }
}

public class CarStatisticsDto
{
    public int TotalCars { get; set; }
    public double TotalCarsChangePercent { get; set; }
    public int Available { get; set; }
    public int OnTrip { get; set; }
    public int Pending { get; set; }
    public int Offline { get; set; }
}
