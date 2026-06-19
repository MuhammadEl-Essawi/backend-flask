
namespace Rently.Management.Domain.Entities;

public class Notification
{
    public int Id { get; set; }

    public int UserId { get; set; }
    public string? Title { get; set; }
    public string? Message { get; set; }
    public string? Type { get; set; }               // "info", "booking", "payment" ...
    public bool IsRead { get; set; }

    public User? User { get; set; }
}