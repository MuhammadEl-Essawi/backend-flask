using Microsoft.AspNetCore.Mvc;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi.DTOs;
using Microsoft.AspNetCore.Authorization;

namespace Rently.Management.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class RequestController : ControllerBase
    {
        private readonly IRequestRepository _requestRepository;
        private readonly IUserRepository _userRepository;
        private readonly ICarRepository _carRepository;

        public RequestController(
            IRequestRepository requestRepository,
            IUserRepository userRepository,
            ICarRepository carRepository)
        {
            _requestRepository = requestRepository;
            _userRepository = userRepository;
            _carRepository = carRepository;
        }

        [HttpGet]
        public async Task<ActionResult<PagedResultDto<RequestDto>>> GetRequests(
            [FromQuery] string? search = null,
            [FromQuery] string? type = null,
            [FromQuery] string? status = null,
            [FromQuery] string? sort = null,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 10)
        {
            var result = await _requestRepository.GetRequestsAsync(search, type, status, sort, page, pageSize);

            var dtos = result.Data.Select(r => new RequestDto
            {
                Id = r.Id,
                Type = r.Type,
                SubmittedBy = r.SubmittedBy,
                SubmittedOn = r.SubmittedOn,
                TotalPrice = r.TotalPrice,
                Status = r.Status
            }).ToList();

            return Ok(new PagedResultDto<RequestDto>
            {
                Data = dtos,
                TotalCount = result.TotalCount,
                Page = result.Page,
                PageSize = result.PageSize,
                TotalPages = result.TotalPages
            });
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<RequestDetailsDto>> GetRequestDetails(
            int id,
            [FromQuery] string type,
            [FromQuery] bool includeDocs = false)
        {
            if (string.Equals(type, "Owner verification", StringComparison.OrdinalIgnoreCase))
            {
                var user = await _userRepository.GetByIdAsync(id);
                if (user == null) return NotFound();

                var dto = new RequestDetailsDto
                {
                    Id = user.Id,
                    Type = "Owner verification",
                    Name = $"{user.FirstName} {user.LastName}".Trim(),
                    Email = user.Email ?? "",
                    PhoneNumber = user.Phone ?? "",
                    SubmittedOn = user.CreatedAt,
                    Status = user.ApprovalStatus ?? "Pending",
                    DrivingLicenseNumber = includeDocs ? user.LicenseNumber : null,
                    IdNumber = includeDocs ? user.ZipCode : null,
                    IdImageUrl = includeDocs ? user.IdImage : null,
                    LicenseImageUrl = includeDocs ? user.LicenseImage : null,
                    SelfieImageUrl = includeDocs ? user.SelfieImage : null
                };

                return Ok(dto);
            }

            if (string.Equals(type, "Car listing", StringComparison.OrdinalIgnoreCase))
            {
                var car = await _carRepository.GetByIdAsync(id);
                if (car == null) return NotFound();

                var dto = new RequestDetailsDto
                {
                    Id = car.Id,
                    Type = "Car listing",
                    Name = car.Owner != null ? $"{car.Owner.FirstName} {car.Owner.LastName}".Trim() : "",
                    Email = car.Owner?.Email ?? "",
                    PhoneNumber = car.Owner?.Phone ?? "",
                    SubmittedOn = car.CreatedAt,
                    Status = car.Status ?? "Pending",
                    DrivingLicenseNumber = includeDocs ? car.Owner?.LicenseNumber : null,
                    IdNumber = includeDocs ? car.LicensePlate : null,
                    IdImageUrl = includeDocs ? car.Owner?.IdImage : null,
                    LicenseImageUrl = includeDocs ? car.CarLicenseImage : null,
                    SelfieImageUrl = includeDocs ? car.Owner?.SelfieImage : null
                };

                return Ok(dto);
            }

            return BadRequest("Unknown request type.");
        }

        [HttpPatch("{id}/status")]
        public async Task<IActionResult> UpdateStatus(int id, [FromBody] UpdateRequestStatusDto dto)
        {
            var success = await _requestRepository.UpdateRequestStatusAsync(id, dto.Type, dto.Status);
            if (!success) return NotFound();

            return NoContent();
        }
    }
}

