using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Rently.Management.Domain.Entities;

namespace Rently.Management.Infrastructure.Data.Configurations
{
    public class CarImageConfiguration : IEntityTypeConfiguration<CarImage>
    {
        public void Configure(EntityTypeBuilder<CarImage> builder)
        {
            builder.ToTable("CarImages");

            builder.HasKey(i => i.Id);
            builder.Property(i => i.Id).ValueGeneratedOnAdd();

            builder.Property(i => i.ImagePath).HasMaxLength(500).IsRequired();

            builder.HasOne(i => i.Car)
                   .WithMany(c => c.Images)
                   .HasForeignKey(i => i.CarId)
                   .OnDelete(DeleteBehavior.Cascade);
        }
    }
}