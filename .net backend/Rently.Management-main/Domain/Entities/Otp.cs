
namespace Rently.Management.Domain.Entities;

public class Otp
{
    public int Id { get; set; }

    public int UserId { get; set; }
    public string? OtpHash { get; set; }            // Hashed OTP for security

    public User? User { get; set; }

    // Optional: add DateTime CreatedAt, DateTime ExpiresAt, bool IsUsed
}
