namespace Rently.Management.WebApi.DTOs
{
    public class WeeklyRevenueDto
    {
        public List<DailyRevenueDto> Data { get; set; } = new();
    }

    public class DailyRevenueDto
    {
        public int Day { get; set; }  // 22, 23, 24, 25, 26, 27, 28
        public decimal Revenue { get; set; }
    }
}
