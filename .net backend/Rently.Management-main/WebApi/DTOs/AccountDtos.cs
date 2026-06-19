using System.ComponentModel.DataAnnotations;

namespace Rently.Management.WebApi.DTOs
{
    public class ChangeNameDto
    {
        [Required]
        [StringLength(150)]
        public string FirstName { get; set; } = "";
        [Required]
        [StringLength(150)]
        public string LastName { get; set; } = "";
    }

    public class ChangePasswordDto
    {
        [Required]
        [MinLength(6)]
        public string CurrentPassword { get; set; } = "";
        [Required]
        [MinLength(12)]
        [RegularExpression(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$")]
        public string NewPassword { get; set; } = "";
    }

    public class RequestResetDto
    {
        [Required]
        [EmailAddress]
        public string Email { get; set; } = "";
    }

    public class ResetPasswordDto
    {
        [Required]
        [EmailAddress]
        public string Email { get; set; } = "";
        [Required]
        public string Token { get; set; } = "";
        [Required]
        [MinLength(12)]
        [RegularExpression(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$")]
        public string NewPassword { get; set; } = "";
    }

    public class AddAdminDto
    {
        [Required]
        [StringLength(150)]
        public string FirstName { get; set; } = "";
        [Required]
        [StringLength(150)]
        public string LastName { get; set; } = "";
        [Required]
        [EmailAddress]
        [StringLength(255)]
        public string Email { get; set; } = "";
        [Required]
        [StringLength(30)]
        public string Phone { get; set; } = "";
        [Required]
        [MinLength(12)]
        [RegularExpression(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$")]
        public string Password { get; set; } = "";
        [Required]
        [StringLength(6, MinimumLength = 6)]
        public string Otp { get; set; } = "";
    }

    public class RequestAddAdminOtpDto
    {
        [Required]
        [EmailAddress]
        public string Email { get; set; } = "";
    }
}
