using System.Net.Http;
using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Configuration;

namespace Rently.Management.WebApi.Services
{
    public class PaymobService
    {
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly IConfiguration _configuration;

        public PaymobService(IHttpClientFactory httpClientFactory, IConfiguration configuration)
        {
            _httpClientFactory = httpClientFactory;
            _configuration = configuration;
        }

        public async Task<string> AuthenticateAsync()
        {
            var apiKey = _configuration["Paymob:ApiKey"] ?? "";
            if (string.IsNullOrWhiteSpace(apiKey) || apiKey.StartsWith("__USE_USER_SECRETS__"))
                throw new InvalidOperationException("Paymob ApiKey is not configured");
            var client = _httpClientFactory.CreateClient("paymob");
            var authUrl = (client.BaseAddress?.ToString().TrimEnd('/') ?? "https://accept.paymob.com/api") + "/auth/tokens";
            var res = await client.PostAsJsonAsync(authUrl, new { api_key = apiKey });
            var body = await res.Content.ReadAsStringAsync();
            if (!res.IsSuccessStatusCode)
                throw new InvalidOperationException($"Paymob auth failed: {(int)res.StatusCode} {res.ReasonPhrase}. Url: {authUrl}. Body: {body}");
            try
            {
                var auth = System.Text.Json.JsonSerializer.Deserialize<AuthRes>(body);
                return auth?.token ?? "";
            }
            catch
            {
                throw new InvalidOperationException($"Invalid Paymob auth response: {body}");
            }
        }

        public async Task<(string orderId, string paymentToken, string url)> InitiateAsync(int amountCents, string currency, string email, string name, string phone, string integrationId, bool useIframe)
        {
            var token = await AuthenticateAsync();
            var client = _httpClientFactory.CreateClient("paymob");

            var orderReq = new
            {
                auth_token = token,
                delivery_needed = false,
                amount_cents = amountCents,
                currency = currency,
                items = Array.Empty<object>()
            };
            var orderUrl = (client.BaseAddress?.ToString().TrimEnd('/') ?? "https://accept.paymob.com/api") + "/ecommerce/orders";
            var orderRes = await client.PostAsJsonAsync(orderUrl, orderReq);
            var order = await orderRes.Content.ReadFromJsonAsync<OrderRes>();

            var redirectionUrl = _configuration["Paymob:RedirectionUrl"] ?? "";
            var billingData = new
            {
                apartment = "NA",
                email = email,
                floor = "NA",
                first_name = name,
                street = "NA",
                building = "NA",
                phone_number = phone,
                shipping_method = "NA",
                postal_code = "NA",
                city = "NA",
                country = "NA",
                last_name = name,
                state = "NA"
            };
            var keyReq = new
            {
                auth_token = token,
                amount_cents = amountCents,
                expiration = 3600,
                order_id = order?.id,
                billing_data = billingData,
                currency = currency,
                integration_id = integrationId,
                lock_order_when_paid = true,
                redirection_url = redirectionUrl
            };
            var keyUrl = (client.BaseAddress?.ToString().TrimEnd('/') ?? "https://accept.paymob.com/api") + "/acceptance/payment_keys";
            var keyRes = await client.PostAsJsonAsync(keyUrl, keyReq);
            var key = await keyRes.Content.ReadFromJsonAsync<PaymentKeyRes>();
            var iframeId = _configuration["Paymob:IframeId"] ?? "";
            var baseUrl = _configuration["Paymob:BaseUrl"] ?? "";
            var root = baseUrl.Replace("/api", "");
            var url = useIframe
                ? $"{root}/acceptance/iframes/{iframeId}?payment_token={key?.token}"
                : $"{root}/acceptance/pay?payment_token={key?.token}";
            return (order?.id?.ToString() ?? "", key?.token ?? "", url);
        }

        public bool ValidateHmac(Dictionary<string, string> fields, string hmac)
        {
            var secret = _configuration["Paymob:HmacSecret"] ?? "";
            var keys = new[]
            {
                "amount_cents","created_at","currency","error_occured","has_parent_transaction","id","integration_id","is_3d_secure","is_auth","is_capture","is_refunded","is_standalone_payment","is_voided","order.id","owner","pending","source_data.pan","source_data.sub_type","source_data.type","success"
            };
            var sb = new StringBuilder();
            foreach (var k in keys)
            {
                if (fields.TryGetValue(k, out var v))
                    sb.Append(v);
            }
            var data = sb.ToString();
            using var sha = new HMACSHA512(Encoding.UTF8.GetBytes(secret));
            var hash = sha.ComputeHash(Encoding.UTF8.GetBytes(data));
            var computed = BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
            return string.Equals(computed, hmac, StringComparison.OrdinalIgnoreCase);
        }

        private class AuthRes { public string? token { get; set; } }
        private class OrderRes { public int? id { get; set; } }
        private class PaymentKeyRes { public string? token { get; set; } }
    }
}
