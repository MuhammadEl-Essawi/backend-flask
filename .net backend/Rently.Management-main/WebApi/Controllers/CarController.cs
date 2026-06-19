using Microsoft.AspNetCore.Mvc;
using Rently.Management.Domain.Entities;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi.DTOs;
using Rently.Management.WebApi.Services;

namespace Rently.Management.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class CarController : ControllerBase
    {
        private readonly ICarRepository _carRepository;
        private readonly IUserRepository _userRepository;
        private readonly WebhookService _webhookService;

        public CarController(ICarRepository carRepository, IUserRepository userRepository, WebhookService webhookService)
        {
            _carRepository = carRepository;
            _userRepository = userRepository;
            _webhookService = webhookService;
        }

        [HttpGet("statistics")]
        public async Task<ActionResult<CarStatisticsDto>> GetStatistics()
        {
            var statistics = await _carRepository.GetStatisticsAsync();

            var dto = new CarStatisticsDto
            {
                TotalCars = statistics.TotalCars,
                TotalCarsChangePercent = statistics.TotalCarsChangePercent,
                Available = statistics.Available,
                OnTrip = statistics.OnTrip,
                Pending = statistics.Pending,
                Offline = statistics.Offline
            };

            return Ok(dto);
        }

        [HttpGet]
        public async Task<ActionResult<PagedResultDto<CarDto>>> GetCars(
            [FromQuery] string? search = null,
            [FromQuery] string? status = null,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 10,
            [FromQuery] bool includePlate = false)
        {
            var result = await _carRepository.GetCarsAsync(search, status, page, pageSize);

            var carDtos = result.Data.Select(c => new CarDto
            {
                Id = c.Id,
                CarName = $"{c.Brand} {c.Model} {c.Year}",
                PlateNumber = includePlate ? (c.LicensePlate ?? "") : "",
                OwnerName = c.Owner != null ? $"{c.Owner.FirstName} {c.Owner.LastName}".Trim() : "",
                PricePerDay = c.PricePerDay,
                Status = c.Status ?? "Pending",
                ImageUrl = c.Images?.FirstOrDefault()?.ImagePath,
                Year = c.Year,
                Brand = c.Brand,
                Model = c.Model
            }).ToList();

            return Ok(new PagedResultDto<CarDto>
            {
                Data = carDtos,
                TotalCount = result.TotalCount,
                Page = result.Page,
                PageSize = result.PageSize,
                TotalPages = result.TotalPages
            });
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<CarDto>> GetCar(int id, [FromQuery] bool includePlate = false)
        {
            var car = await _carRepository.GetByIdAsync(id);

            if (car == null)
            {
                return NotFound();
            }

            return Ok(new CarDto
            {
                Id = car.Id,
                CarName = $"{car.Brand} {car.Model} {car.Year}",
                PlateNumber = includePlate ? (car.LicensePlate ?? "") : "",
                OwnerName = car.Owner != null ? $"{car.Owner.FirstName} {car.Owner.LastName}".Trim() : "",
                PricePerDay = car.PricePerDay,
                Status = car.Status ?? "Pending",
                ImageUrl = car.Images?.FirstOrDefault()?.ImagePath,
                Year = car.Year,
                Brand = car.Brand,
                Model = car.Model
            });
        }

        [HttpPost]
        public async Task<ActionResult<CarDto>> CreateCar([FromBody] CreateCarDto dto)
        {
            // Verify owner exists
            var owner = await _userRepository.GetByIdAsync(dto.OwnerId);
            if (owner == null)
            {
                return BadRequest(new { message = $"User with ID {dto.OwnerId} does not exist." });
            }

            var car = new Car
            {
                OwnerId = dto.OwnerId,
                Brand = dto.Brand,
                Model = dto.Model,
                Year = dto.Year,
                PricePerDay = dto.PricePerDay,
                Status = dto.Status ?? "Pending",
                Transmission = dto.Transmission,
                Color = dto.Color,
                LocationCity = dto.LocationCity,
                Features = dto.Features,
                Description = dto.Description,
                LicensePlate = dto.LicensePlate,
                CarLicenseImage = dto.CarLicenseImage
            };

            var createdCar = await _carRepository.CreateAsync(car);
            
            // Reload with includes
            var carWithDetails = await _carRepository.GetByIdAsync(createdCar.Id);
            _ = _webhookService.PublishAsync("car.created", new { car_id = createdCar.Id, owner_id = createdCar.OwnerId, brand = createdCar.Brand, model = createdCar.Model, year = createdCar.Year, status = createdCar.Status, price_per_day = createdCar.PricePerDay });

            return CreatedAtAction(nameof(GetCar), new { id = createdCar.Id }, new CarDto
            {
                Id = createdCar.Id,
                CarName = $"{createdCar.Brand} {createdCar.Model} {createdCar.Year}",
                PlateNumber = createdCar.LicensePlate ?? "",
                OwnerName = carWithDetails?.Owner != null ? $"{carWithDetails.Owner.FirstName} {carWithDetails.Owner.LastName}".Trim() : "",
                PricePerDay = createdCar.PricePerDay,
                Status = createdCar.Status ?? "Pending",
                ImageUrl = carWithDetails?.Images?.FirstOrDefault()?.ImagePath,
                Year = createdCar.Year,
                Brand = createdCar.Brand,
                Model = createdCar.Model
            });
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateCar(int id, [FromBody] UpdateCarDto dto)
        {
            var car = await _carRepository.GetByIdAsync(id);

            if (car == null)
            {
                return NotFound();
            }

            if (!string.IsNullOrEmpty(dto.Brand))
                car.Brand = dto.Brand;
            if (!string.IsNullOrEmpty(dto.Model))
                car.Model = dto.Model;
            if (dto.Year.HasValue)
                car.Year = dto.Year.Value;
            if (dto.PricePerDay.HasValue)
                car.PricePerDay = dto.PricePerDay.Value;
            if (!string.IsNullOrEmpty(dto.Status))
                car.Status = dto.Status;
            if (!string.IsNullOrEmpty(dto.Transmission))
                car.Transmission = dto.Transmission;
            if (!string.IsNullOrEmpty(dto.Color))
                car.Color = dto.Color;
            if (!string.IsNullOrEmpty(dto.LocationCity))
                car.LocationCity = dto.LocationCity;
            if (!string.IsNullOrEmpty(dto.Features))
                car.Features = dto.Features;
            if (!string.IsNullOrEmpty(dto.Description))
                car.Description = dto.Description;
            if (!string.IsNullOrEmpty(dto.LicensePlate))
                car.LicensePlate = dto.LicensePlate;

            await _carRepository.UpdateAsync(car);
            _ = _webhookService.PublishAsync("car.updated", new { car_id = car.Id, owner_id = car.OwnerId, brand = car.Brand, model = car.Model, year = car.Year, status = car.Status, price_per_day = car.PricePerDay });

            return NoContent();
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteCar(int id)
        {
            var car = await _carRepository.GetByIdAsync(id);
            if (car == null)
            {
                return NotFound();
            }

            await _carRepository.DeleteAsync(car);

            return NoContent();
        }

        [HttpPatch("{id}/status")]
        public async Task<IActionResult> UpdateCarStatus(int id, [FromBody] UpdateStatusDto dto)
        {
            var car = await _carRepository.GetByIdAsync(id);
            if (car == null)
            {
                return NotFound();
            }

            car.Status = dto.Status;
            await _carRepository.UpdateAsync(car);
            _ = _webhookService.PublishAsync("car.status_changed", new { car_id = car.Id, status = car.Status });

            return NoContent();
        }
    }
}
