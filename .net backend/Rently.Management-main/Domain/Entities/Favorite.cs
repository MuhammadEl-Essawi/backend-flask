
namespace Rently.Management.Domain.Entities;

public class Favorite
{
    public int Id { get; set; }

    public int UserId { get; set; }
    public int CarId { get; set; }

    public User? User { get; set; }
    public Car? Car { get; set; }
}