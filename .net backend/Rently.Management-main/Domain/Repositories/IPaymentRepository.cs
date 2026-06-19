using Rently.Management.Domain.Entities;

namespace Rently.Management.Domain.Repositories;

public interface IPaymentRepository
{
    Task<Payment?> GetByIdAsync(int id);
    Task<PagedResult<Payment>> GetTransactionsAsync(string? search, string? type, string? status, int page, int pageSize);
    Task<PagedResult<Payment>> GetOwnerPayoutsAsync(int page, int pageSize);
    Task<PagedResult<Payment>> GetRefundsAsync(string? status, int page, int pageSize);
    Task<PaymentStatistics> GetStatisticsAsync();
    Task<Payment> CreateAsync(Payment payment);
    Task<Payment> UpdateAsync(Payment payment);
    Task<bool> ExistsAsync(int id);
}

public class PaymentStatistics
{
    public decimal TotalRevenue { get; set; }
    public double TotalRevenueChangePercent { get; set; }
    public decimal PendingPayout { get; set; }
    public decimal ProfitLast30Days { get; set; }
    public double ProfitChangePercent { get; set; }
}
