using System.ComponentModel.DataAnnotations;
namespace Rently.Management.WebApi.DTOs
{
    public class PaymobInitRequestDto
    {
        [Required]
        [Range(1, int.MaxValue)]
        public int BookingId { get; set; }
        public int? UserId { get; set; }
        [Required]
        [Range(typeof(decimal), "0.01", "79228162514264337593543950335")]
        public decimal Amount { get; set; }
        [Required]
        public string Currency { get; set; } = "EGP";
        [Required]
        [EmailAddress]
        public string Email { get; set; } = "";
        [Required]
        public string FirstName { get; set; } = "";
        [Required]
        public string LastName { get; set; } = "";
        public string FullName => $"{FirstName} {LastName}".Trim();
        [Required]
        public string Phone { get; set; } = "";
        [Required]
        [RegularExpression("^(card|wallet)$")]
        public string Method { get; set; } = "card";
    }
}
