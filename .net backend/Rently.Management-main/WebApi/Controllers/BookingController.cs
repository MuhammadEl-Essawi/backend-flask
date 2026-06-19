using Microsoft.AspNetCore.Mvc;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi.DTOs;

namespace Rently.Management.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class BookingController : ControllerBase
    {
        private readonly IBookingRepository _bookingRepository;

        public BookingController(IBookingRepository bookingRepository)
        {
            _bookingRepository = bookingRepository;
        }

        [HttpGet("statistics")]
        public async Task<ActionResult<BookingStatisticsDto>> GetStatistics()
        {
            var statistics = await _bookingRepository.GetStatisticsAsync();

            return Ok(new BookingStatisticsDto
            {
                ActiveTrips = statistics.ActiveTrips,
                PickUpToday = statistics.PickUpToday,
                ReturnToday = statistics.ReturnToday,
                Canceled = statistics.Canceled
            });
        }

        [HttpGet]
        public async Task<ActionResult<PagedResultDto<BookingDto>>> GetBookings(
            [FromQuery] string? search = null,
            [FromQuery] string? status = null,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 10)
        {
            var result = await _bookingRepository.GetBookingsAsync(search, status, page, pageSize);

            var bookingDtos = result.Data.Select(b =>
            {
                var carName = $"{b.Car?.Brand} {b.Car?.Model} {b.Car?.Year}".Trim();
                if (string.IsNullOrWhiteSpace(carName)) carName = "";

                return new BookingDto
                {
                    Id = b.Id,
                    BookingId = b.TransactionId ?? b.Id.ToString(),
                    CarName = carName,
                    CarImageUrl = b.Car?.Images?.FirstOrDefault()?.ImagePath,
                    RenterName = b.Renter != null ? $"{b.Renter.FirstName} {b.Renter.LastName}".Trim() : "",
                    OwnerName = b.Car?.Owner != null ? $"{b.Car.Owner.FirstName} {b.Car.Owner.LastName}".Trim() : "",
                    StartDate = b.StartDate,
                    EndDate = b.EndDate,
                    Days = Math.Max(1, (int)Math.Ceiling((b.EndDate.Date - b.StartDate.Date).TotalDays)),
                    TotalPrice = b.TotalPrice,
                    Status = ToUiStatus(b.Status, b.StartDate, b.EndDate)
                };
            }).ToList();

            return Ok(new PagedResultDto<BookingDto>
            {
                Data = bookingDtos,
                TotalCount = result.TotalCount,
                Page = result.Page,
                PageSize = result.PageSize,
                TotalPages = result.TotalPages
            });
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<BookingDto>> GetBooking(int id)
        {
            var booking = await _bookingRepository.GetByIdAsync(id);
            if (booking == null) return NotFound();

            var carName = $"{booking.Car?.Brand} {booking.Car?.Model} {booking.Car?.Year}".Trim();
            if (string.IsNullOrWhiteSpace(carName)) carName = "";

            return Ok(new BookingDto
            {
                Id = booking.Id,
                BookingId = booking.TransactionId ?? booking.Id.ToString(),
                CarName = carName,
                CarImageUrl = booking.Car?.Images?.FirstOrDefault()?.ImagePath,
                RenterName = booking.Renter != null ? $"{booking.Renter.FirstName} {booking.Renter.LastName}".Trim() : "",
                OwnerName = booking.Car?.Owner != null ? $"{booking.Car.Owner.FirstName} {booking.Car.Owner.LastName}".Trim() : "",
                StartDate = booking.StartDate,
                EndDate = booking.EndDate,
                Days = Math.Max(1, (int)Math.Ceiling((booking.EndDate.Date - booking.StartDate.Date).TotalDays)),
                TotalPrice = booking.TotalPrice,
                Status = ToUiStatus(booking.Status, booking.StartDate, booking.EndDate)
            });
        }

        [HttpPatch("{id}/status")]
        public async Task<IActionResult> UpdateBookingStatus(int id, [FromBody] UpdateBookingStatusDto dto)
        {
            var booking = await _bookingRepository.GetByIdAsync(id);
            if (booking == null) return NotFound();

            booking.Status = FromUiStatus(dto.Status);
            await _bookingRepository.UpdateAsync(booking);

            return NoContent();
        }

        [HttpPost("refund-all")]
        public async Task<IActionResult> RefundAll([FromBody] RefundBookingsDto dto)
        {
            var count = await _bookingRepository.RefundBookingsAsync(dto.BookingIds, dto.Reason);
            return Ok(new { refundedBookings = count });
        }

        private static string ToUiStatus(string? status, DateTime start, DateTime end)
        {
            var today = DateTime.UtcNow.Date;

            if (string.Equals(status, "Cancelled", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(status, "Canceled", StringComparison.OrdinalIgnoreCase))
                return "Canceled";

            if (string.Equals(status, "Pending", StringComparison.OrdinalIgnoreCase))
                return "Pending";

            if (string.Equals(status, "Completed", StringComparison.OrdinalIgnoreCase) || end.Date < today)
                return "Completed";

            // For Confirmed/Active or unknown: infer by dates
            if (start.Date > today) return "Up coming";
            if (start.Date <= today && end.Date >= today) return "Active";

            return "Up coming";
        }

        private static string FromUiStatus(string status)
        {
            status = (status ?? "").Trim();

            return status switch
            {
                "Active" => "Active",
                "Up coming" => "Confirmed",
                "Upcoming" => "Confirmed",
                "Completed" => "Completed",
                "Canceled" => "Cancelled",
                "Cancelled" => "Cancelled",
                "Pending" => "Pending",
                _ => "Pending"
            };
        }
    }
}

