using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Configuration;
using Rently.Management.WebApi.Serialization;

namespace Rently.Management.WebApi.Services
{
    public class WebhookService
    {
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly IConfiguration _configuration;
        private readonly JsonSerializerOptions _jsonOptions;

        public WebhookService(IHttpClientFactory httpClientFactory, IConfiguration configuration)
        {
            _httpClientFactory = httpClientFactory;
            _configuration = configuration;
            _jsonOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = new SnakeCaseNamingPolicy()
            };
        }

        public async Task PublishAsync(string eventName, object payload)
        {
            var enabled = (_configuration["Webhooks:Flask:Enabled"] ?? "false").Equals("true", StringComparison.OrdinalIgnoreCase);
            var url = _configuration["Webhooks:Flask:Url"] ?? "";
            var secret = _configuration["Webhooks:Flask:Secret"] ?? "";
            if (!enabled) return;
            if (string.IsNullOrWhiteSpace(url)) return;

            var envelope = new
            {
                id = Guid.NewGuid().ToString("N"),
                @event = eventName,
                created_at = DateTime.UtcNow,
                data = payload
            };

            var body = JsonSerializer.Serialize(envelope, _jsonOptions);
            var signature = ComputeHmac(body, secret);
            try
            {
                var client = _httpClientFactory.CreateClient();
                var content = new StringContent(body, Encoding.UTF8, "application/json");
                content.Headers.Add("X-Rently-Event", eventName);
                content.Headers.Add("X-Rently-Signature", signature);
                await client.PostAsync(url, content);
            }
            catch
            {
            }
        }

        private static string ComputeHmac(string data, string secret)
        {
            var key = Encoding.UTF8.GetBytes(secret ?? "");
            using var hmac = new HMACSHA256(key);
            var bytes = Encoding.UTF8.GetBytes(data);
            var hash = hmac.ComputeHash(bytes);
            var sb = new StringBuilder(hash.Length * 2);
            foreach (var b in hash)
                sb.Append(b.ToString("x2"));
            return sb.ToString();
        }
    }
}
