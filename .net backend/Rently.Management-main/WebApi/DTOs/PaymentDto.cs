using System.ComponentModel.DataAnnotations;
namespace Rently.Management.WebApi.DTOs;

public class PaymentStatisticsDto
{
    public decimal TotalRevenue { get; set; }
    public double TotalRevenueChangePercent { get; set; }
    public decimal PendingPayout { get; set; }
    public decimal ProfitLast30Days { get; set; }
    public double ProfitChangePercent { get; set; }
}

public class PaymentDto
{
    public int Id { get; set; }
    public string TxId { get; set; } = ""; // ProviderPaymentId or formatted ID
    public DateTime Date { get; set; }
    public string Type { get; set; } = ""; // "Reservation payment", "Owner Payout", "Refund", "New booking"
    public string PayerName { get; set; } = "";
    public string PayeeName { get; set; } = "";
    public decimal Amount { get; set; }
    public string Status { get; set; } = ""; // "Succeeded", "Pending", "Failed"
    public string Currency { get; set; } = "EGP";
    public int? BookingId { get; set; }
}

public class OwnerPayoutDto
{
    public int Id { get; set; }
    public string OwnerName { get; set; } = "";
    public DateTime LastPayout { get; set; }
    public decimal Amount { get; set; }
    public string Status { get; set; } = "";
    public string Currency { get; set; } = "EGP";
}

public class RefundDto
{
    public int Id { get; set; }
    public string RenterName { get; set; } = "";
    public decimal RefundAmount { get; set; }
    public string Status { get; set; } = ""; // "Under Review", "Approved", "Rejected", "Completed"
    public DateTime CreatedAt { get; set; }
    public string? Reason { get; set; }
    public int BookingId { get; set; }
}

public class CreatePaymentDto
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
    public string Status { get; set; } = "Pending";
    public string? Provider { get; set; }
    public string? ProviderPaymentId { get; set; }
    public string? ProviderReceiptUrl { get; set; }
}

public class UpdatePaymentDto
{
    public string? Status { get; set; }
    public string? ProviderPaymentId { get; set; }
    public string? ProviderReceiptUrl { get; set; }
    public string? FailureCode { get; set; }
    public string? FailureMessage { get; set; }
}

public class ProcessPayoutDto
{
    [Required]
    [Range(1, int.MaxValue)]
    public int OwnerId { get; set; }
    [Required]
    [Range(typeof(decimal), "0.01", "79228162514264337593543950335")]
    public decimal Amount { get; set; }
    public string? Provider { get; set; }
}

public class ProcessRefundDto
{
    [Required]
    [Range(1, int.MaxValue)]
    public int PaymentId { get; set; }
    [Required]
    [Range(typeof(decimal), "0.01", "79228162514264337593543950335")]
    public decimal Amount { get; set; }
    public string? Reason { get; set; }
}
