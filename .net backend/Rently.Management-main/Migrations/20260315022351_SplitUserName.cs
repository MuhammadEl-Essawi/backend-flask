using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Rently.Management.Migrations
{
    /// <inheritdoc />
    public partial class SplitUserName : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.RenameColumn(
                name: "name",
                table: "Users",
                newName: "last_name");

            migrationBuilder.AddColumn<string>(
                name: "first_name",
                table: "Users",
                type: "nvarchar(150)",
                maxLength: 150,
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "first_name",
                table: "Users");

            migrationBuilder.RenameColumn(
                name: "last_name",
                table: "Users",
                newName: "name");
        }
    }
}
