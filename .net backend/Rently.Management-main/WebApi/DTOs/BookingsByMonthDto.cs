namespace Rently.Management.WebApi.DTOs
{
    public class BookingsByMonthDto
    {
        public List<MonthlyBookingDto> Data { get; set; } = new();
    }

    public class MonthlyBookingDto
    {
        public string Month { get; set; } = string.Empty;  // "Jan", "Feb", "Mar", etc.
        public int Count { get; set; }
    }
}
