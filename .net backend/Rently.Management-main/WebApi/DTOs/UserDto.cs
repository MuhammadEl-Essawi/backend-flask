using System.ComponentModel.DataAnnotations;
namespace Rently.Management.WebApi.DTOs;

public class UserDto
{
    public int Id { get; set; }
    public string FirstName { get; set; } = "";
    public string LastName { get; set; } = "";
    public string FullName => $"{FirstName} {LastName}".Trim();
    public string Email { get; set; } = "";
    public string Status { get; set; } = "";
}

public class CreateUserDto
{
    [Required]
    [StringLength(150)]
    public string? FirstName { get; set; }
    [Required]
    [StringLength(150)]
    public string? LastName { get; set; }
    [Required]
    [EmailAddress]
    [StringLength(255)]
    public string? Email { get; set; }
    [Required]
    [StringLength(30)]
    public string? Phone { get; set; }
    [Required]
    [StringLength(50)]
    public string? Role { get; set; }
    public string? ApprovalStatus { get; set; }
}

public class UpdateUserDto
{
    [StringLength(150)]
    public string? FirstName { get; set; }
    [StringLength(150)]
    public string? LastName { get; set; }
    [EmailAddress]
    [StringLength(255)]
    public string? Email { get; set; }
    [StringLength(30)]
    public string? Phone { get; set; }
    public string? ApprovalStatus { get; set; }
}

public class UpdateStatusDto
{
    [Required]
    [RegularExpression("^(Active|Non-Active|Blocked)$")]
    public string Status { get; set; } = ""; // "Active", "Non-Active", "Blocked"
}

public class PagedResultDto<T>
{
    public List<T> Data { get; set; } = new();
    public int TotalCount { get; set; }
    public int Page { get; set; }
    public int PageSize { get; set; }
    public int TotalPages { get; set; }
}
