// Domain/Entities/CarImage.cs
namespace Rently.Management.Domain.Entities;

public class CarImage
{
    public int Id { get; set; }

    public int CarId { get; set; }
    public string? ImagePath { get; set; }          // URL or file path

    public Car? Car { get; set; }
}
