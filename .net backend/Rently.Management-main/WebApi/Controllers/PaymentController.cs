using Microsoft.AspNetCore.Mvc;
using Rently.Management.Domain.Entities;
using Rently.Management.Domain.Repositories;
using Rently.Management.WebApi.DTOs;
using Rently.Management.WebApi.Services;
using Microsoft.AspNetCore.Authorization;
using System.Text.Json;
using System.Security.Cryptography;
using System.Text;

namespace Rently.Management.WebApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PaymentController : ControllerBase
    {
        /// <summary>
        /// Payments management and Paymob gateway (statistics, transactions, refunds, callback/webhook).
        /// This controller exposes card/wallet flows and uses HMAC to validate Paymob responses.
        /// </summary>
        private readonly IPaymentRepository _paymentRepository;
        private readonly IBookingRepository _bookingRepository;
        private readonly IUserRepository _userRepository;
        private readonly PaymobService _paymobService;
        private readonly IConfiguration _configuration;
        private readonly WebhookService _webhookService;

        public PaymentController(IPaymentRepository paymentRepository, IBookingRepository bookingRepository, IUserRepository userRepository, PaymobService paymobService, IConfiguration configuration, WebhookService webhookService)
        {
            _paymentRepository = paymentRepository;
            _bookingRepository = bookingRepository;
            _userRepository = userRepository;
            _paymobService = paymobService;
            _configuration = configuration;
            _webhookService = webhookService;
        }

        [HttpGet("statistics")]
        public async Task<ActionResult<PaymentStatisticsDto>> GetStatistics()
        {
            var statistics = await _paymentRepository.GetStatisticsAsync();

            var dto = new PaymentStatisticsDto
            {
                TotalRevenue = statistics.TotalRevenue,
                TotalRevenueChangePercent = statistics.TotalRevenueChangePercent,
                PendingPayout = statistics.PendingPayout,
                ProfitLast30Days = statistics.ProfitLast30Days,
                ProfitChangePercent = statistics.ProfitChangePercent
            };

            return Ok(dto);
        }

        [HttpPost("paymob/init")]
        [Authorize]
        /// <summary>
        /// Initialize payment via Paymob and return orderId, paymentToken, and payment URL.
        /// method: card (renders iframe) or wallet (redirect flow).
        /// </summary>
        public async Task<ActionResult<object>> InitPaymob([FromBody] PaymobInitRequestDto dto)
        {
            // Verify booking exists
            var bookingExists = await _bookingRepository.ExistsAsync(dto.BookingId);
            if (!bookingExists)
            {
                return BadRequest(new { message = $"Booking with ID {dto.BookingId} does not exist." });
            }

            // Verify user exists
            if (dto.UserId.HasValue && dto.UserId.Value > 0)
            {
                var userExists = await _userRepository.ExistsAsync(dto.UserId.Value);
                if (!userExists)
                {
                    return BadRequest(new { message = $"User with ID {dto.UserId.Value} does not exist." });
                }
            }

            var amountCents = (int)(dto.Amount * 100);
            var method = (dto.Method ?? "card").ToLowerInvariant();
            var integrationId = method == "wallet"
                ? _configuration["Paymob:IntegrationIdWallet"] ?? ""
                : _configuration["Paymob:IntegrationIdCard"] ?? "";
            var useIframe = method != "wallet";
            var (orderId, paymentToken, url) = await _paymobService.InitiateAsync(amountCents, dto.Currency, dto.Email, dto.FullName, dto.Phone, integrationId, useIframe);
            var payment = new Payment
            {
                BookingId = dto.BookingId,
                UserId = dto.UserId,
                Amount = dto.Amount,
                Currency = dto.Currency,
                Status = "Pending",
                Provider = "Paymob",
                ProviderPaymentId = orderId,
                ProviderReceiptUrl = url
            };
            var created = await _paymentRepository.CreateAsync(payment);
            _ = _webhookService.PublishAsync("payment.created", new { payment_id = created.Id, booking_id = created.BookingId, user_id = created.UserId, amount = created.Amount, currency = created.Currency, status = created.Status, provider = created.Provider, provider_payment_id = created.ProviderPaymentId });
            return Ok(new { payment_id = created.Id, order_id = orderId, payment_token = paymentToken, url, method });
        }

        [HttpGet("paymob/checkout")]
        [Authorize]
        /// <summary>
        /// Direct payment route: returns iframe for card or Redirect for wallet.
        /// Saves a Pending payment and returns HTML or Redirect.
        /// </summary>
        public async Task<IActionResult> CheckoutPaymob(
            [FromQuery] int bookingId,
            [FromQuery] int? userId,
            [FromQuery] decimal amount,
            [FromQuery] string currency = "EGP",
            [FromQuery] string email = "",
            [FromQuery] string firstName = "",
            [FromQuery] string lastName = "",
            [FromQuery] string phone = "",
            [FromQuery] string method = "card")
        {
            // Verify booking exists
            var bookingExists = await _bookingRepository.ExistsAsync(bookingId);
            if (!bookingExists)
            {
                return BadRequest(new { message = $"Booking with ID {bookingId} does not exist." });
            }

            // Verify user exists
            if (userId.HasValue && userId.Value > 0)
            {
                var userExists = await _userRepository.ExistsAsync(userId.Value);
                if (!userExists)
                {
                    return BadRequest(new { message = $"User with ID {userId.Value} does not exist." });
                }
            }

            var amountCents = (int)(amount * 100);
            method = (method ?? "card").ToLowerInvariant();
            var integrationId = method == "wallet"
                ? _configuration["Paymob:IntegrationIdWallet"] ?? ""
                : _configuration["Paymob:IntegrationIdCard"] ?? "";
            var useIframe = method != "wallet";
            var fullName = $"{firstName} {lastName}".Trim();
            var (orderId, paymentToken, url) = await _paymobService.InitiateAsync(amountCents, currency, email, fullName, phone, integrationId, useIframe);
            var payment = new Payment
            {
                BookingId = bookingId,
                UserId = userId,
                Amount = amount,
                Currency = currency,
                Status = "Pending",
                Provider = "Paymob",
                ProviderPaymentId = orderId,
                ProviderReceiptUrl = url
            };
            await _paymentRepository.CreateAsync(payment);
            _ = _webhookService.PublishAsync("payment.created", new { payment_id = payment.Id, booking_id = payment.BookingId, user_id = payment.UserId, amount = payment.Amount, currency = payment.Currency, status = payment.Status, provider = payment.Provider, provider_payment_id = payment.ProviderPaymentId });

            if (useIframe)
            {
                var html = $"<html><head><meta charset=\"utf-8\"/><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/></head><body style=\"margin:0;padding:0\"><iframe src=\"{url}\" style=\"border:0;width:100%;height:100vh\"></iframe></body></html>";
                return Content(html, "text/html");
            }
            else
            {
                return Redirect(url);
            }
        }

        [HttpGet("test/iframe")]
        [AllowAnonymous]
        /// <summary>
        /// Test rendering an iframe for any URL (quick experiments).
        /// </summary>
        public IActionResult TestIframe([FromQuery] string url)
        {
            if (string.IsNullOrWhiteSpace(url)) return BadRequest();
            var html = $"<html><head><meta charset=\"utf-8\"/><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/></head><body style=\"margin:0;padding:0\"><iframe src=\"{url}\" style=\"border:0;width:100%;height:100vh\"></iframe></body></html>";
            return Content(html, "text/html");
        }

        [HttpGet("paymob/callback")]
        [AllowAnonymous]
        /// <summary>
        /// Paymob callback after payment (GET).
        /// Validates HMAC, updates payment status, and notifies partner if configured.
        /// </summary>
        public async Task<IActionResult> PaymobCallback()
        {
            var hmac = Request.Query["hmac"].ToString();
            var dict = Request.Query.ToDictionary(k => k.Key, v => v.Value.ToString());
            var valid = _paymobService.ValidateHmac(dict, hmac);
            if (!valid) return BadRequest();
            var success = dict.TryGetValue("success", out var s) && s == "true";
            var orderId = dict.TryGetValue("order", out var o) ? o : "";
            var payment = (await _paymentRepository.GetTransactionsAsync(orderId, "All", null, 1, 1)).Data.FirstOrDefault();
            if (payment != null)
            {
                payment.Status = success ? "Succeeded" : "Failed";
                await _paymentRepository.UpdateAsync(payment);
                await NotifyPartnerAsync(payment);
                _ = _webhookService.PublishAsync("payment.updated", new { payment_id = payment.Id, booking_id = payment.BookingId, status = payment.Status, amount = payment.Amount, currency = payment.Currency, provider_payment_id = payment.ProviderPaymentId });
            }
            return Ok();
        }

        [HttpPost("paymob/webhook")]
        [AllowAnonymous]
        /// <summary>
        /// Paymob webhook (POST).
        /// Validates HMAC, updates payment status, and notifies partner via PartnerWebhookUrl.
        /// </summary>
        public async Task<IActionResult> PaymobWebhook()
        {
            using var reader = new StreamReader(Request.Body);
            var body = await reader.ReadToEndAsync();
            var json = JsonDocument.Parse(body);
            var obj = json.RootElement;
            var hmac = Request.Query["hmac"].ToString();
            var fields = new Dictionary<string, string>();
            void add(string path, string key)
            {
                try
                {
                    var parts = path.Split('.');
                    var cur = obj;
                    foreach (var p in parts)
                        cur = cur.GetProperty(p);
                    fields[key] = cur.ToString();
                }
                catch { }
            }
            add("obj.amount_cents", "amount_cents");
            add("obj.created_at", "created_at");
            add("obj.currency", "currency");
            add("obj.error_occured", "error_occured");
            add("obj.has_parent_transaction", "has_parent_transaction");
            add("obj.id", "id");
            add("obj.integration_id", "integration_id");
            add("obj.is_3d_secure", "is_3d_secure");
            add("obj.is_auth", "is_auth");
            add("obj.is_capture", "is_capture");
            add("obj.is_refunded", "is_refunded");
            add("obj.is_standalone_payment", "is_standalone_payment");
            add("obj.is_voided", "is_voided");
            add("obj.order.id", "order.id");
            add("obj.owner", "owner");
            add("obj.pending", "pending");
            add("obj.source_data.pan", "source_data.pan");
            add("obj.source_data.sub_type", "source_data.sub_type");
            add("obj.source_data.type", "source_data.type");
            add("obj.success", "success");
            var valid = _paymobService.ValidateHmac(fields, hmac);
            if (!valid) return BadRequest();
            var orderId = fields.TryGetValue("order.id", out var oid) ? oid : "";
            var success = fields.TryGetValue("success", out var sv) && sv == "true";
            var payment = (await _paymentRepository.GetTransactionsAsync(orderId, "All", null, 1, 1)).Data.FirstOrDefault();
            if (payment != null)
            {
                payment.Status = success ? "Succeeded" : "Failed";
                payment.ProviderPaymentId = fields.TryGetValue("id", out var pid) ? pid : payment.ProviderPaymentId;
                await _paymentRepository.UpdateAsync(payment);
                await NotifyPartnerAsync(payment);
                _ = _webhookService.PublishAsync("payment.updated", new { payment_id = payment.Id, booking_id = payment.BookingId, status = payment.Status, amount = payment.Amount, currency = payment.Currency, provider_payment_id = payment.ProviderPaymentId });
            }
            return Ok();
        }

        private async Task NotifyPartnerAsync(Payment payment)
        {
            var url = _configuration["Paymob:PartnerWebhookUrl"];
            if (string.IsNullOrWhiteSpace(url)) return;
            using var client = new HttpClient();
            var payload = new
            {
                payment_id = payment.Id,
                booking_id = payment.BookingId,
                status = payment.Status,
                amount = payment.Amount,
                currency = payment.Currency,
                provider_payment_id = payment.ProviderPaymentId
            };
            try { await client.PostAsJsonAsync(url, payload); } catch { }
        }
        [HttpGet("transactions")]
        /// <summary>
        /// Return payments with filtering and paging.
        /// </summary>
        public async Task<ActionResult<PagedResultDto<PaymentDto>>> GetTransactions(
            [FromQuery] string? search = null,
            [FromQuery] string? type = null,
            [FromQuery] string? status = null,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 10)
        {
            var result = await _paymentRepository.GetTransactionsAsync(search, type, status, page, pageSize);

            var paymentDtos = result.Data.Select(p => new PaymentDto
            {
                Id = p.Id,
                TxId = p.ProviderPaymentId ?? p.Id.ToString(),
                Date = p.CreatedAt,
                Type = GetPaymentType(p),
                PayerName = (p.Booking?.Renter != null ? $"{p.Booking.Renter.FirstName} {p.Booking.Renter.LastName}".Trim() : (p.User != null ? $"{p.User.FirstName} {p.User.LastName}".Trim() : "")),
                PayeeName = (p.Booking?.Car?.Owner != null ? $"{p.Booking.Car.Owner.FirstName} {p.Booking.Car.Owner.LastName}".Trim() : ""),
                Amount = p.Amount,
                Status = p.Status,
                Currency = p.Currency,
                BookingId = p.BookingId
            }).ToList();

            return Ok(new PagedResultDto<PaymentDto>
            {
                Data = paymentDtos,
                TotalCount = result.TotalCount,
                Page = result.Page,
                PageSize = result.PageSize,
                TotalPages = result.TotalPages
            });
        }

        [HttpGet("owner-payouts")]
        public async Task<ActionResult<PagedResultDto<OwnerPayoutDto>>> GetOwnerPayouts(
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 10)
        {
            var result = await _paymentRepository.GetOwnerPayoutsAsync(page, pageSize);

            var payoutDtos = result.Data
                .GroupBy(p => p.Booking!.Car!.OwnerId)
                .Select(g => new OwnerPayoutDto
                {
                    Id = g.Key,
                    OwnerName = g.First().Booking!.Car!.Owner != null ? $"{g.First().Booking!.Car!.Owner!.FirstName} {g.First().Booking!.Car!.Owner!.LastName}".Trim() : "",
                    LastPayout = g.Max(p => p.CreatedAt),
                    Amount = g.Sum(p => p.Amount),
                    Status = "Completed",
                    Currency = g.First().Currency
                })
                .ToList();

            return Ok(new PagedResultDto<OwnerPayoutDto>
            {
                Data = payoutDtos,
                TotalCount = payoutDtos.Count,
                Page = page,
                PageSize = pageSize,
                TotalPages = (int)Math.Ceiling(payoutDtos.Count / (double)pageSize)
            });
        }

        [HttpGet("refunds")]
        public async Task<ActionResult<PagedResultDto<RefundDto>>> GetRefunds(
            [FromQuery] string? status = null,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 10)
        {
            var result = await _paymentRepository.GetRefundsAsync(status, page, pageSize);

            var refundDtos = result.Data.Select(p => new RefundDto
            {
                Id = p.Id,
                RenterName = p.Booking?.Renter != null ? $"{p.Booking.Renter.FirstName} {p.Booking.Renter.LastName}".Trim() : "",
                RefundAmount = p.Amount,
                Status = GetRefundStatus(p.Status),
                CreatedAt = p.CreatedAt,
                Reason = p.FailureMessage,
                BookingId = p.BookingId
            }).ToList();

            return Ok(new PagedResultDto<RefundDto>
            {
                Data = refundDtos,
                TotalCount = result.TotalCount,
                Page = result.Page,
                PageSize = result.PageSize,
                TotalPages = result.TotalPages
            });
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<PaymentDto>> GetPayment(int id)
        {
            var payment = await _paymentRepository.GetByIdAsync(id);

            if (payment == null)
            {
                return NotFound();
            }

            return Ok(new PaymentDto
            {
                Id = payment.Id,
                TxId = payment.ProviderPaymentId ?? payment.Id.ToString(),
                Date = payment.CreatedAt,
                Type = GetPaymentType(payment),
                PayerName = (payment.Booking?.Renter != null ? $"{payment.Booking.Renter.FirstName} {payment.Booking.Renter.LastName}".Trim() : (payment.User != null ? $"{payment.User.FirstName} {payment.User.LastName}".Trim() : "")),
                PayeeName = (payment.Booking?.Car?.Owner != null ? $"{payment.Booking.Car.Owner.FirstName} {payment.Booking.Car.Owner.LastName}".Trim() : ""),
                Amount = payment.Amount,
                Status = payment.Status,
                Currency = payment.Currency,
                BookingId = payment.BookingId
            });
        }

        [HttpPost]
        public async Task<ActionResult<PaymentDto>> CreatePayment([FromBody] CreatePaymentDto dto)
        {
            var payment = new Payment
            {
                BookingId = dto.BookingId,
                UserId = dto.UserId,
                Amount = dto.Amount,
                Currency = dto.Currency,
                Status = dto.Status,
                Provider = dto.Provider,
                ProviderPaymentId = dto.ProviderPaymentId,
                ProviderReceiptUrl = dto.ProviderReceiptUrl
            };

            var createdPayment = await _paymentRepository.CreateAsync(payment);
            _ = _webhookService.PublishAsync("payment.created", new { payment_id = createdPayment.Id, booking_id = createdPayment.BookingId, user_id = createdPayment.UserId, amount = createdPayment.Amount, currency = createdPayment.Currency, status = createdPayment.Status, provider = createdPayment.Provider, provider_payment_id = createdPayment.ProviderPaymentId });
            var paymentWithDetails = await _paymentRepository.GetByIdAsync(createdPayment.Id);

            return CreatedAtAction(nameof(GetPayment), new { id = createdPayment.Id }, new PaymentDto
            {
                Id = createdPayment.Id,
                TxId = createdPayment.ProviderPaymentId ?? createdPayment.Id.ToString(),
                Date = createdPayment.CreatedAt,
                Type = GetPaymentType(paymentWithDetails!),
                PayerName = (paymentWithDetails?.Booking?.Renter != null ? $"{paymentWithDetails.Booking.Renter.FirstName} {paymentWithDetails.Booking.Renter.LastName}".Trim() : (paymentWithDetails?.User != null ? $"{paymentWithDetails.User.FirstName} {paymentWithDetails.User.LastName}".Trim() : "")),
                PayeeName = (paymentWithDetails?.Booking?.Car?.Owner != null ? $"{paymentWithDetails.Booking.Car.Owner.FirstName} {paymentWithDetails.Booking.Car.Owner.LastName}".Trim() : ""),
                Amount = createdPayment.Amount,
                Status = createdPayment.Status,
                Currency = createdPayment.Currency,
                BookingId = createdPayment.BookingId
            });
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> UpdatePayment(int id, [FromBody] UpdatePaymentDto dto)
        {
            var payment = await _paymentRepository.GetByIdAsync(id);

            if (payment == null)
            {
                return NotFound();
            }

            if (!string.IsNullOrEmpty(dto.Status))
                payment.Status = dto.Status;
            if (!string.IsNullOrEmpty(dto.ProviderPaymentId))
                payment.ProviderPaymentId = dto.ProviderPaymentId;
            if (!string.IsNullOrEmpty(dto.ProviderReceiptUrl))
                payment.ProviderReceiptUrl = dto.ProviderReceiptUrl;
            if (!string.IsNullOrEmpty(dto.FailureCode))
                payment.FailureCode = dto.FailureCode;
            if (!string.IsNullOrEmpty(dto.FailureMessage))
                payment.FailureMessage = dto.FailureMessage;

            await _paymentRepository.UpdateAsync(payment);
            _ = _webhookService.PublishAsync("payment.updated", new { payment_id = payment.Id, status = payment.Status, provider_payment_id = payment.ProviderPaymentId, provider_receipt_url = payment.ProviderReceiptUrl, failure_code = payment.FailureCode, failure_message = payment.FailureMessage });

            return NoContent();
        }

        [HttpPost("process-payout")]
        public async Task<IActionResult> ProcessPayout([FromBody] ProcessPayoutDto dto)
        {
            // This would typically create a payment record for owner payout
            // Implementation depends on your business logic
            return Ok(new { message = "Payout processed successfully" });
        }

        [HttpPost("process-refund")]
        public async Task<IActionResult> ProcessRefund([FromBody] ProcessRefundDto dto)
        {
            var payment = await _paymentRepository.GetByIdAsync(dto.PaymentId);

            if (payment == null)
            {
                return NotFound();
            }

            // Create refund payment
            var refund = new Payment
            {
                BookingId = payment.BookingId,
                UserId = payment.UserId,
                Amount = dto.Amount,
                Currency = payment.Currency,
                Status = "Pending",
                Provider = payment.Provider,
                FailureMessage = dto.Reason
            };

            await _paymentRepository.CreateAsync(refund);

            // Update original payment status
            payment.Status = "Refunding";
            await _paymentRepository.UpdateAsync(payment);
            _ = _webhookService.PublishAsync("payment.refund_requested", new { payment_id = payment.Id, refund_amount = dto.Amount, status = payment.Status });

            return Ok(new { message = "Refund request created successfully", refundId = refund.Id });
        }

        [HttpPost("refund-all")]
        public async Task<IActionResult> RefundAll([FromBody] List<int> paymentIds)
        {
            foreach (var paymentId in paymentIds)
            {
                var payment = await _paymentRepository.GetByIdAsync(paymentId);
                if (payment != null && payment.Status == "Succeeded")
                {
                    payment.Status = "Refunding";
                    await _paymentRepository.UpdateAsync(payment);
                    _ = _webhookService.PublishAsync("payment.refund_requested", new { payment_id = payment.Id, status = payment.Status });
                }
            }

            return Ok(new { message = "Refund requests processed successfully" });
        }

        private string GetPaymentType(Payment? payment)
        {
            if (payment == null) return "Unknown";

            if (payment.Status == "Refunded" || payment.Status == "Refunding")
                return "Refund";

            if (payment.Booking != null)
            {
                if (payment.CreatedAt >= DateTime.UtcNow.AddDays(-7))
                    return "New booking";
                return "Reservation payment";
            }

            return "Owner Payout";
        }

        private string GetRefundStatus(string paymentStatus)
        {
            return paymentStatus switch
            {
                "Pending" => "Under Review",
                "Refunding" => "Approved",
                "Refunded" => "Completed",
                "Failed" => "Rejected",
                _ => "Under Review"
            };
        }
    }
}
