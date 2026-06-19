using Microsoft.AspNetCore.Mvc;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi.DTOs;

namespace Rently.Management.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class DashboardController : ControllerBase
    {
        private readonly IDashboardRepository _dashboardRepository;

        public DashboardController(IDashboardRepository dashboardRepository)
        {
            _dashboardRepository = dashboardRepository;
        }

        [HttpGet("stats")]
        public async Task<ActionResult<DashboardStatsDto>> GetStats()
        {
            var stats = await _dashboardRepository.GetStatsAsync();

            var dto = new DashboardStatsDto
            {
                TotalUsers = stats.TotalUsers,
                UsersChangePercent = stats.UsersChangePercent,
                TotalCars = stats.TotalCars,
                CarsChangePercent = stats.CarsChangePercent,
                TotalBookings = stats.TotalBookings,
                BookingsChangePercent = stats.BookingsChangePercent,
                ProfitLast30Days = stats.ProfitLast30Days,
                ProfitChangePercent = stats.ProfitChangePercent
            };

            return Ok(dto);
        }

        [HttpGet("weekly-revenue")]
        public async Task<ActionResult<WeeklyRevenueDto>> GetWeeklyRevenue([FromQuery] int days = 7)
        {
            var dailyRevenues = await _dashboardRepository.GetWeeklyRevenueAsync(days);

            var result = new WeeklyRevenueDto();
            foreach (var dailyRevenue in dailyRevenues)
            {
                result.Data.Add(new DailyRevenueDto
                {
                    Day = dailyRevenue.Date.Day,
                    Revenue = dailyRevenue.Revenue
                });
            }

            return Ok(result);
        }

        [HttpGet("bookings-by-month")]
        public async Task<ActionResult<BookingsByMonthDto>> GetBookingsByMonth([FromQuery] int months = 6)
        {
            var monthlyBookings = await _dashboardRepository.GetBookingsByMonthAsync(months);

            var monthNames = new[] { "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" };
            
            var result = new BookingsByMonthDto();
            foreach (var booking in monthlyBookings)
            {
                result.Data.Add(new MonthlyBookingDto
                {
                    Month = monthNames[booking.Month - 1],
                    Count = booking.Count
                });
            }

            return Ok(result);
        }
    }
}
