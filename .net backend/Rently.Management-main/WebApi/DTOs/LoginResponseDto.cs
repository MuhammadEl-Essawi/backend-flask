namespace Rently.Management.WebApi.DTOs
{
    public class LoginResponseDto
    {
        public string Token { get; set; } = "";
        public string? FirstName { get; set; }
        public string? LastName { get; set; }
        public string? FullName => $"{FirstName} {LastName}".Trim();
        public string? Email { get; set; }
        public string? Role { get; set; }
        public bool IsSuperAdmin { get; set; }
        public int UserId { get; set; }
    }
}
