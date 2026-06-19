using System.Net;
using System.Net.Mail;
using Microsoft.Extensions.Configuration;

namespace Rently.Management.WebApi.Services;

public class EmailService : IEmailService
{
    private readonly IConfiguration _configuration;

    public EmailService(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public async Task SendEmailAsync(string to, string subject, string body)
    {
        var smtpConfig = _configuration.GetSection("Smtp");
        var host = smtpConfig["Host"] ?? "smtp.gmail.com";
        var port = int.TryParse(smtpConfig["Port"], out var p) ? p : 587;
        var email = smtpConfig["Email"] ?? "";
        var password = smtpConfig["Password"] ?? "";
        var enableSsl = bool.TryParse(smtpConfig["EnableSsl"], out var ssl) && ssl;

        using var client = new SmtpClient(host, port)
        {
            Credentials = new NetworkCredential(email, password),
            EnableSsl = enableSsl
        };

        var mailMessage = new MailMessage
        {
            From = new MailAddress(email, "Rently Management"),
            Subject = subject,
            Body = body,
            IsBodyHtml = true
        };

        mailMessage.To.Add(to);

        await client.SendMailAsync(mailMessage);
    }
}
