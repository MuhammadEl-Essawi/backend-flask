
namespace Rently.Management.Domain.Entities;

public class CarUnavailableDate
{
    public int Id { get; set; }

    public int CarId { get; set; }
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
    public string? Reason { get; set; }

    public Car? Car { get; set; }
}