
namespace Rently.Management.WebApi.DTOs
{
    public class DashboardStatsDto
    {
        public int TotalUsers { get; set; }
        public double UsersChangePercent { get; set; }  // +5.0

        public int TotalCars { get; set; }
        public double CarsChangePercent { get; set; }

        public int TotalBookings { get; set; }
        public double BookingsChangePercent { get; set; }

        public decimal ProfitLast30Days { get; set; }
        public decimal ProfitChangePercent { get; set; }
    }
}