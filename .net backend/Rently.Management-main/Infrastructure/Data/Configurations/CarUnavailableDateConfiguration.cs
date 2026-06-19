using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Rently.Management.Domain.Entities;

namespace Rently.Management.Infrastructure.Data.Configurations
{
    public class CarUnavailableDateConfiguration : IEntityTypeConfiguration<CarUnavailableDate>
    {
        public void Configure(EntityTypeBuilder<CarUnavailableDate> builder)
        {
            builder.ToTable("CarUnavailableDates");

            builder.HasKey(d => d.Id);
            builder.Property(d => d.Id).ValueGeneratedOnAdd();

            builder.Property(d => d.Reason).HasMaxLength(200);

            builder.HasOne(d => d.Car)
                   .WithMany(c => c.UnavailableDates)
                   .HasForeignKey(d => d.CarId)
                   .OnDelete(DeleteBehavior.Cascade);
        }
    }
}