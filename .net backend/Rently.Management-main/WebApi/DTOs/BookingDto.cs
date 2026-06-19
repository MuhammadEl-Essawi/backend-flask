using System.ComponentModel.DataAnnotations;
namespace Rently.Management.WebApi.DTOs;

public class BookingStatisticsDto
{
    public int ActiveTrips { get; set; }
    public int PickUpToday { get; set; }
    public int ReturnToday { get; set; }
    public int Canceled { get; set; }
}

public class BookingDto
{
    public int Id { get; set; }
    public string BookingId { get; set; } = ""; // TransactionId or Id
    public string CarName { get; set; } = "";   // "Kia Sportage 2019"
    public string? CarImageUrl { get; set; }
    public string RenterName { get; set; } = "";
    public string OwnerName { get; set; } = "";
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
    public int Days { get; set; }
    public decimal TotalPrice { get; set; }
    public string Status { get; set; } = "";    // UI: Active, Up coming, Completed, Canceled, Pending
}

public class UpdateBookingStatusDto
{
    [Required]
    [RegularExpression("^(Active|Up coming|Completed|Canceled|Pending)$")]
    public string Status { get; set; } = ""; // UI status
}

public class RefundBookingsDto
{
    [Required]
    [MinLength(1)]
    public List<int> BookingIds { get; set; } = new();
    public string? Reason { get; set; }
}

