using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Rently.Management.Migrations
{
    /// <inheritdoc />
    public partial class SnakeCaseColumns : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Bookings_Cars_CarId",
                table: "Bookings");

            migrationBuilder.DropForeignKey(
                name: "FK_Bookings_Users_RenterId",
                table: "Bookings");

            migrationBuilder.DropForeignKey(
                name: "FK_CarImages_Cars_CarId",
                table: "CarImages");

            migrationBuilder.DropForeignKey(
                name: "FK_Cars_Users_OwnerId",
                table: "Cars");

            migrationBuilder.DropForeignKey(
                name: "FK_CarUnavailableDates_Cars_CarId",
                table: "CarUnavailableDates");

            migrationBuilder.DropForeignKey(
                name: "FK_Favorites_Cars_CarId",
                table: "Favorites");

            migrationBuilder.DropForeignKey(
                name: "FK_Favorites_Users_UserId",
                table: "Favorites");

            migrationBuilder.DropForeignKey(
                name: "FK_Messages_Users_ReceiverId",
                table: "Messages");

            migrationBuilder.DropForeignKey(
                name: "FK_Messages_Users_SenderId",
                table: "Messages");

            migrationBuilder.DropForeignKey(
                name: "FK_Notifications_Users_UserId",
                table: "Notifications");

            migrationBuilder.DropForeignKey(
                name: "FK_Otps_Users_UserId",
                table: "Otps");

            migrationBuilder.DropForeignKey(
                name: "FK_Payments_Bookings_BookingId",
                table: "Payments");

            migrationBuilder.DropForeignKey(
                name: "FK_Payments_Users_UserId",
                table: "Payments");

            migrationBuilder.DropForeignKey(
                name: "FK_Reviews_Cars_CarId",
                table: "Reviews");

            migrationBuilder.DropForeignKey(
                name: "FK_Reviews_Users_RenterId",
                table: "Reviews");

            migrationBuilder.DropIndex(
                name: "IX_Users_Email",
                table: "Users");

            migrationBuilder.DropIndex(
                name: "IX_Users_LicenseNumber",
                table: "Users");

            migrationBuilder.DropIndex(
                name: "IX_Users_Phone",
                table: "Users");

            migrationBuilder.DropIndex(
                name: "IX_Bookings_TransactionId",
                table: "Bookings");

            migrationBuilder.RenameColumn(
                name: "Role",
                table: "Users",
                newName: "role");

            migrationBuilder.RenameColumn(
                name: "Phone",
                table: "Users",
                newName: "phone");

            migrationBuilder.RenameColumn(
                name: "Nationality",
                table: "Users",
                newName: "nationality");

            migrationBuilder.RenameColumn(
                name: "Name",
                table: "Users",
                newName: "name");

            migrationBuilder.RenameColumn(
                name: "Email",
                table: "Users",
                newName: "email");

            migrationBuilder.RenameColumn(
                name: "Id",
                table: "Users",
                newName: "id");

            migrationBuilder.RenameColumn(
                name: "ZipCode",
                table: "Users",
                newName: "zip_code");

            migrationBuilder.RenameColumn(
                name: "UpdatedAt",
                table: "Users",
                newName: "updated_at");

            migrationBuilder.RenameColumn(
                name: "SelfieImage",
                table: "Users",
                newName: "selfie_image");

            migrationBuilder.RenameColumn(
                name: "ResidenceProofImage",
                table: "Users",
                newName: "residence_proof_image");

            migrationBuilder.RenameColumn(
                name: "PreferredLanguage",
                table: "Users",
                newName: "preferred_language");

            migrationBuilder.RenameColumn(
                name: "PayoutMethod",
                table: "Users",
                newName: "payout_method");

            migrationBuilder.RenameColumn(
                name: "PayoutDetails",
                table: "Users",
                newName: "payout_details");

            migrationBuilder.RenameColumn(
                name: "PassportImage",
                table: "Users",
                newName: "passport_image");

            migrationBuilder.RenameColumn(
                name: "LicenseNumber",
                table: "Users",
                newName: "license_number");

            migrationBuilder.RenameColumn(
                name: "LicenseImage",
                table: "Users",
                newName: "license_image");

            migrationBuilder.RenameColumn(
                name: "JobProofImage",
                table: "Users",
                newName: "job_proof_image");

            migrationBuilder.RenameColumn(
                name: "IdImage",
                table: "Users",
                newName: "id_image");

            migrationBuilder.RenameColumn(
                name: "CreatedAt",
                table: "Users",
                newName: "created_at");

            migrationBuilder.RenameColumn(
                name: "BillingCountry",
                table: "Users",
                newName: "billing_country");

            migrationBuilder.RenameColumn(
                name: "ApprovalStatus",
                table: "Users",
                newName: "approval_status");

            migrationBuilder.RenameColumn(
                name: "Rating",
                table: "Reviews",
                newName: "rating");

            migrationBuilder.RenameColumn(
                name: "Comment",
                table: "Reviews",
                newName: "comment");

            migrationBuilder.RenameColumn(
                name: "Id",
                table: "Reviews",
                newName: "id");

            migrationBuilder.RenameColumn(
                name: "UpdatedAt",
                table: "Reviews",
                newName: "updated_at");

            migrationBuilder.RenameColumn(
                name: "RenterId",
                table: "Reviews",
                newName: "renter_id");

            migrationBuilder.RenameColumn(
                name: "CreatedAt",
                table: "Reviews",
                newName: "created_at");

            migrationBuilder.RenameColumn(
                name: "CarId",
                table: "Reviews",
                newName: "car_id");

            migrationBuilder.RenameIndex(
                name: "IX_Reviews_RenterId",
                table: "Reviews",
                newName: "IX_Reviews_renter_id");

            migrationBuilder.RenameIndex(
                name: "IX_Reviews_CarId",
                table: "Reviews",
                newName: "IX_Reviews_car_id");

            migrationBuilder.RenameColumn(
                name: "Status",
                table: "Payments",
                newName: "status");

            migrationBuilder.RenameColumn(
                name: "Provider",
                table: "Payments",
                newName: "provider");

            migrationBuilder.RenameColumn(
                name: "Currency",
                table: "Payments",
                newName: "currency");

            migrationBuilder.RenameColumn(
                name: "Amount",
                table: "Payments",
                newName: "amount");

            migrationBuilder.RenameColumn(
                name: "Id",
                table: "Payments",
                newName: "id");

            migrationBuilder.RenameColumn(
                name: "UserId",
                table: "Payments",
                newName: "user_id");

            migrationBuilder.RenameColumn(
                name: "UpdatedAt",
                table: "Payments",
                newName: "updated_at");

            migrationBuilder.RenameColumn(
                name: "ProviderReceiptUrl",
                table: "Payments",
                newName: "provider_receipt_url");

            migrationBuilder.RenameColumn(
                name: "ProviderPaymentId",
                table: "Payments",
                newName: "provider_payment_id");

            migrationBuilder.RenameColumn(
                name: "FailureMessage",
                table: "Payments",
                newName: "failure_message");

            migrationBuilder.RenameColumn(
                name: "FailureCode",
                table: "Payments",
                newName: "failure_code");

            migrationBuilder.RenameColumn(
                name: "CreatedAt",
                table: "Payments",
                newName: "created_at");

            migrationBuilder.RenameColumn(
                name: "BookingId",
                table: "Payments",
                newName: "booking_id");

            migrationBuilder.RenameIndex(
                name: "IX_Payments_UserId",
                table: "Payments",
                newName: "IX_Payments_user_id");

            migrationBuilder.RenameIndex(
                name: "IX_Payments_ProviderPaymentId",
                table: "Payments",
                newName: "IX_Payments_provider_payment_id");

            migrationBuilder.RenameIndex(
                name: "IX_Payments_BookingId",
                table: "Payments",
                newName: "IX_Payments_booking_id");

            migrationBuilder.RenameColumn(
                name: "Id",
                table: "Otps",
                newName: "id");

            migrationBuilder.RenameColumn(
                name: "UserId",
                table: "Otps",
                newName: "user_id");

            migrationBuilder.RenameColumn(
                name: "OtpHash",
                table: "Otps",
                newName: "otp_hash");

            migrationBuilder.RenameIndex(
                name: "IX_Otps_UserId",
                table: "Otps",
                newName: "IX_Otps_user_id");

            migrationBuilder.RenameColumn(
                name: "Type",
                table: "Notifications",
                newName: "type");

            migrationBuilder.RenameColumn(
                name: "Title",
                table: "Notifications",
                newName: "title");

            migrationBuilder.RenameColumn(
                name: "Message",
                table: "Notifications",
                newName: "message");

            migrationBuilder.RenameColumn(
                name: "Id",
                table: "Notifications",
                newName: "id");

            migrationBuilder.RenameColumn(
                name: "UserId",
                table: "Notifications",
                newName: "user_id");

            migrationBuilder.RenameColumn(
                name: "IsRead",
                table: "Notifications",
                newName: "is_read");

            migrationBuilder.RenameIndex(
                name: "IX_Notifications_UserId",
                table: "Notifications",
                newName: "IX_Notifications_user_id");

            migrationBuilder.RenameColumn(
                name: "Content",
                table: "Messages",
                newName: "content");

            migrationBuilder.RenameColumn(
                name: "Id",
                table: "Messages",
                newName: "id");

            migrationBuilder.RenameColumn(
                name: "SenderId",
                table: "Messages",
                newName: "sender_id");

            migrationBuilder.RenameColumn(
                name: "ReceiverId",
                table: "Messages",
                newName: "receiver_id");

            migrationBuilder.RenameColumn(
                name: "IsRead",
                table: "Messages",
                newName: "is_read");

            migrationBuilder.RenameIndex(
                name: "IX_Messages_SenderId",
                table: "Messages",
                newName: "IX_Messages_sender_id");

            migrationBuilder.RenameIndex(
                name: "IX_Messages_ReceiverId",
                table: "Messages",
                newName: "IX_Messages_receiver_id");

            migrationBuilder.RenameColumn(
                name: "Id",
                table: "Favorites",
                newName: "id");

            migrationBuilder.RenameColumn(
                name: "CarId",
                table: "Favorites",
                newName: "car_id");

            migrationBuilder.RenameColumn(
                name: "UserId",
                table: "Favorites",
                newName: "user_id");

            migrationBuilder.RenameIndex(
                name: "IX_Favorites_CarId",
                table: "Favorites",
                newName: "IX_Favorites_car_id");

            migrationBuilder.RenameColumn(
                name: "Reason",
                table: "CarUnavailableDates",
                newName: "reason");

            migrationBuilder.RenameColumn(
                name: "Id",
                table: "CarUnavailableDates",
                newName: "id");

            migrationBuilder.RenameColumn(
                name: "StartDate",
                table: "CarUnavailableDates",
                newName: "start_date");

            migrationBuilder.RenameColumn(
                name: "EndDate",
                table: "CarUnavailableDates",
                newName: "end_date");

            migrationBuilder.RenameColumn(
                name: "CarId",
                table: "CarUnavailableDates",
                newName: "car_id");

            migrationBuilder.RenameIndex(
                name: "IX_CarUnavailableDates_CarId",
                table: "CarUnavailableDates",
                newName: "IX_CarUnavailableDates_car_id");

            migrationBuilder.RenameColumn(
                name: "Year",
                table: "Cars",
                newName: "year");

            migrationBuilder.RenameColumn(
                name: "Transmission",
                table: "Cars",
                newName: "transmission");

            migrationBuilder.RenameColumn(
                name: "Status",
                table: "Cars",
                newName: "status");

            migrationBuilder.RenameColumn(
                name: "Model",
                table: "Cars",
                newName: "model");

            migrationBuilder.RenameColumn(
                name: "Features",
                table: "Cars",
                newName: "features");

            migrationBuilder.RenameColumn(
                name: "Description",
                table: "Cars",
                newName: "description");

            migrationBuilder.RenameColumn(
                name: "Color",
                table: "Cars",
                newName: "color");

            migrationBuilder.RenameColumn(
                name: "Brand",
                table: "Cars",
                newName: "brand");

            migrationBuilder.RenameColumn(
                name: "Id",
                table: "Cars",
                newName: "id");

            migrationBuilder.RenameColumn(
                name: "UpdatedAt",
                table: "Cars",
                newName: "updated_at");

            migrationBuilder.RenameColumn(
                name: "PricePerDay",
                table: "Cars",
                newName: "price_per_day");

            migrationBuilder.RenameColumn(
                name: "OwnerId",
                table: "Cars",
                newName: "owner_id");

            migrationBuilder.RenameColumn(
                name: "LocationCity",
                table: "Cars",
                newName: "location_city");

            migrationBuilder.RenameColumn(
                name: "LicensePlate",
                table: "Cars",
                newName: "license_plate");

            migrationBuilder.RenameColumn(
                name: "CreatedAt",
                table: "Cars",
                newName: "created_at");

            migrationBuilder.RenameColumn(
                name: "CarLicenseImage",
                table: "Cars",
                newName: "car_license_image");

            migrationBuilder.RenameColumn(
                name: "AverageRating",
                table: "Cars",
                newName: "average_rating");

            migrationBuilder.RenameIndex(
                name: "IX_Cars_OwnerId",
                table: "Cars",
                newName: "IX_Cars_owner_id");

            migrationBuilder.RenameIndex(
                name: "IX_Cars_LicensePlate",
                table: "Cars",
                newName: "IX_Cars_license_plate");

            migrationBuilder.RenameColumn(
                name: "Id",
                table: "CarImages",
                newName: "id");

            migrationBuilder.RenameColumn(
                name: "ImagePath",
                table: "CarImages",
                newName: "image_path");

            migrationBuilder.RenameColumn(
                name: "CarId",
                table: "CarImages",
                newName: "car_id");

            migrationBuilder.RenameIndex(
                name: "IX_CarImages_CarId",
                table: "CarImages",
                newName: "IX_CarImages_car_id");

            migrationBuilder.RenameColumn(
                name: "Status",
                table: "Bookings",
                newName: "status");

            migrationBuilder.RenameColumn(
                name: "Id",
                table: "Bookings",
                newName: "id");

            migrationBuilder.RenameColumn(
                name: "UpdatedAt",
                table: "Bookings",
                newName: "updated_at");

            migrationBuilder.RenameColumn(
                name: "TransactionId",
                table: "Bookings",
                newName: "transaction_id");

            migrationBuilder.RenameColumn(
                name: "TotalPrice",
                table: "Bookings",
                newName: "total_price");

            migrationBuilder.RenameColumn(
                name: "StartDate",
                table: "Bookings",
                newName: "start_date");

            migrationBuilder.RenameColumn(
                name: "RenterId",
                table: "Bookings",
                newName: "renter_id");

            migrationBuilder.RenameColumn(
                name: "PaymentConfirmedAt",
                table: "Bookings",
                newName: "payment_confirmed_at");

            migrationBuilder.RenameColumn(
                name: "PaidAmount",
                table: "Bookings",
                newName: "paid_amount");

            migrationBuilder.RenameColumn(
                name: "EndDate",
                table: "Bookings",
                newName: "end_date");

            migrationBuilder.RenameColumn(
                name: "CreatedAt",
                table: "Bookings",
                newName: "created_at");

            migrationBuilder.RenameColumn(
                name: "CarId",
                table: "Bookings",
                newName: "car_id");

            migrationBuilder.RenameIndex(
                name: "IX_Bookings_RenterId",
                table: "Bookings",
                newName: "IX_Bookings_renter_id");

            migrationBuilder.RenameIndex(
                name: "IX_Bookings_CarId",
                table: "Bookings",
                newName: "IX_Bookings_car_id");

            migrationBuilder.RenameColumn(
                name: "PasswordHash",
                table: "Users",
                newName: "password_hash");

            migrationBuilder.RenameColumn(
                name: "PasswordSalt",
                table: "Users",
                newName: "password_salt");

            migrationBuilder.RenameColumn(
                name: "PasswordResetToken",
                table: "Users",
                newName: "password_reset_token");

            migrationBuilder.RenameColumn(
                name: "PasswordResetTokenExpires",
                table: "Users",
                newName: "password_reset_token_expires");

            migrationBuilder.CreateIndex(
                name: "IX_Users_email",
                table: "Users",
                column: "email",
                unique: true,
                filter: "[email] IS NOT NULL");

            migrationBuilder.CreateIndex(
                name: "IX_Users_license_number",
                table: "Users",
                column: "license_number",
                unique: true,
                filter: "[license_number] IS NOT NULL");

            migrationBuilder.CreateIndex(
                name: "IX_Users_phone",
                table: "Users",
                column: "phone",
                unique: true,
                filter: "[phone] IS NOT NULL");

            migrationBuilder.CreateIndex(
                name: "IX_Bookings_transaction_id",
                table: "Bookings",
                column: "transaction_id",
                unique: true,
                filter: "[transaction_id] IS NOT NULL");

            migrationBuilder.AddForeignKey(
                name: "FK_Bookings_Cars_car_id",
                table: "Bookings",
                column: "car_id",
                principalTable: "Cars",
                principalColumn: "id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Bookings_Users_renter_id",
                table: "Bookings",
                column: "renter_id",
                principalTable: "Users",
                principalColumn: "id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_CarImages_Cars_car_id",
                table: "CarImages",
                column: "car_id",
                principalTable: "Cars",
                principalColumn: "id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Cars_Users_owner_id",
                table: "Cars",
                column: "owner_id",
                principalTable: "Users",
                principalColumn: "id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_CarUnavailableDates_Cars_car_id",
                table: "CarUnavailableDates",
                column: "car_id",
                principalTable: "Cars",
                principalColumn: "id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Favorites_Cars_car_id",
                table: "Favorites",
                column: "car_id",
                principalTable: "Cars",
                principalColumn: "id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Favorites_Users_user_id",
                table: "Favorites",
                column: "user_id",
                principalTable: "Users",
                principalColumn: "id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Messages_Users_receiver_id",
                table: "Messages",
                column: "receiver_id",
                principalTable: "Users",
                principalColumn: "id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Messages_Users_sender_id",
                table: "Messages",
                column: "sender_id",
                principalTable: "Users",
                principalColumn: "id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Notifications_Users_user_id",
                table: "Notifications",
                column: "user_id",
                principalTable: "Users",
                principalColumn: "id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Otps_Users_user_id",
                table: "Otps",
                column: "user_id",
                principalTable: "Users",
                principalColumn: "id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Payments_Bookings_booking_id",
                table: "Payments",
                column: "booking_id",
                principalTable: "Bookings",
                principalColumn: "id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Payments_Users_user_id",
                table: "Payments",
                column: "user_id",
                principalTable: "Users",
                principalColumn: "id",
                onDelete: ReferentialAction.SetNull);

            migrationBuilder.AddForeignKey(
                name: "FK_Reviews_Cars_car_id",
                table: "Reviews",
                column: "car_id",
                principalTable: "Cars",
                principalColumn: "id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Reviews_Users_renter_id",
                table: "Reviews",
                column: "renter_id",
                principalTable: "Users",
                principalColumn: "id",
                onDelete: ReferentialAction.Restrict);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Bookings_Cars_car_id",
                table: "Bookings");

            migrationBuilder.DropForeignKey(
                name: "FK_Bookings_Users_renter_id",
                table: "Bookings");

            migrationBuilder.DropForeignKey(
                name: "FK_CarImages_Cars_car_id",
                table: "CarImages");

            migrationBuilder.DropForeignKey(
                name: "FK_Cars_Users_owner_id",
                table: "Cars");

            migrationBuilder.DropForeignKey(
                name: "FK_CarUnavailableDates_Cars_car_id",
                table: "CarUnavailableDates");

            migrationBuilder.DropForeignKey(
                name: "FK_Favorites_Cars_car_id",
                table: "Favorites");

            migrationBuilder.DropForeignKey(
                name: "FK_Favorites_Users_user_id",
                table: "Favorites");

            migrationBuilder.DropForeignKey(
                name: "FK_Messages_Users_receiver_id",
                table: "Messages");

            migrationBuilder.DropForeignKey(
                name: "FK_Messages_Users_sender_id",
                table: "Messages");

            migrationBuilder.DropForeignKey(
                name: "FK_Notifications_Users_user_id",
                table: "Notifications");

            migrationBuilder.DropForeignKey(
                name: "FK_Otps_Users_user_id",
                table: "Otps");

            migrationBuilder.DropForeignKey(
                name: "FK_Payments_Bookings_booking_id",
                table: "Payments");

            migrationBuilder.DropForeignKey(
                name: "FK_Payments_Users_user_id",
                table: "Payments");

            migrationBuilder.DropForeignKey(
                name: "FK_Reviews_Cars_car_id",
                table: "Reviews");

            migrationBuilder.DropForeignKey(
                name: "FK_Reviews_Users_renter_id",
                table: "Reviews");

            migrationBuilder.DropIndex(
                name: "IX_Users_email",
                table: "Users");

            migrationBuilder.DropIndex(
                name: "IX_Users_license_number",
                table: "Users");

            migrationBuilder.DropIndex(
                name: "IX_Users_phone",
                table: "Users");

            migrationBuilder.DropIndex(
                name: "IX_Bookings_transaction_id",
                table: "Bookings");

            migrationBuilder.RenameColumn(
                name: "password_hash",
                table: "Users",
                newName: "PasswordHash");

            migrationBuilder.RenameColumn(
                name: "password_salt",
                table: "Users",
                newName: "PasswordSalt");

            migrationBuilder.RenameColumn(
                name: "password_reset_token",
                table: "Users",
                newName: "PasswordResetToken");

            migrationBuilder.RenameColumn(
                name: "password_reset_token_expires",
                table: "Users",
                newName: "PasswordResetTokenExpires");

            migrationBuilder.RenameColumn(
                name: "role",
                table: "Users",
                newName: "Role");

            migrationBuilder.RenameColumn(
                name: "phone",
                table: "Users",
                newName: "Phone");

            migrationBuilder.RenameColumn(
                name: "nationality",
                table: "Users",
                newName: "Nationality");

            migrationBuilder.RenameColumn(
                name: "name",
                table: "Users",
                newName: "Name");

            migrationBuilder.RenameColumn(
                name: "email",
                table: "Users",
                newName: "Email");

            migrationBuilder.RenameColumn(
                name: "id",
                table: "Users",
                newName: "Id");

            migrationBuilder.RenameColumn(
                name: "zip_code",
                table: "Users",
                newName: "ZipCode");

            migrationBuilder.RenameColumn(
                name: "updated_at",
                table: "Users",
                newName: "UpdatedAt");

            migrationBuilder.RenameColumn(
                name: "selfie_image",
                table: "Users",
                newName: "SelfieImage");

            migrationBuilder.RenameColumn(
                name: "residence_proof_image",
                table: "Users",
                newName: "ResidenceProofImage");

            migrationBuilder.RenameColumn(
                name: "preferred_language",
                table: "Users",
                newName: "PreferredLanguage");

            migrationBuilder.RenameColumn(
                name: "payout_method",
                table: "Users",
                newName: "PayoutMethod");

            migrationBuilder.RenameColumn(
                name: "payout_details",
                table: "Users",
                newName: "PayoutDetails");

            migrationBuilder.RenameColumn(
                name: "passport_image",
                table: "Users",
                newName: "PassportImage");

            migrationBuilder.RenameColumn(
                name: "license_number",
                table: "Users",
                newName: "LicenseNumber");

            migrationBuilder.RenameColumn(
                name: "license_image",
                table: "Users",
                newName: "LicenseImage");

            migrationBuilder.RenameColumn(
                name: "job_proof_image",
                table: "Users",
                newName: "JobProofImage");

            migrationBuilder.RenameColumn(
                name: "id_image",
                table: "Users",
                newName: "IdImage");

            migrationBuilder.RenameColumn(
                name: "created_at",
                table: "Users",
                newName: "CreatedAt");

            migrationBuilder.RenameColumn(
                name: "billing_country",
                table: "Users",
                newName: "BillingCountry");

            migrationBuilder.RenameColumn(
                name: "approval_status",
                table: "Users",
                newName: "ApprovalStatus");

            migrationBuilder.RenameColumn(
                name: "rating",
                table: "Reviews",
                newName: "Rating");

            migrationBuilder.RenameColumn(
                name: "comment",
                table: "Reviews",
                newName: "Comment");

            migrationBuilder.RenameColumn(
                name: "id",
                table: "Reviews",
                newName: "Id");

            migrationBuilder.RenameColumn(
                name: "updated_at",
                table: "Reviews",
                newName: "UpdatedAt");

            migrationBuilder.RenameColumn(
                name: "renter_id",
                table: "Reviews",
                newName: "RenterId");

            migrationBuilder.RenameColumn(
                name: "created_at",
                table: "Reviews",
                newName: "CreatedAt");

            migrationBuilder.RenameColumn(
                name: "car_id",
                table: "Reviews",
                newName: "CarId");

            migrationBuilder.RenameIndex(
                name: "IX_Reviews_renter_id",
                table: "Reviews",
                newName: "IX_Reviews_RenterId");

            migrationBuilder.RenameIndex(
                name: "IX_Reviews_car_id",
                table: "Reviews",
                newName: "IX_Reviews_CarId");

            migrationBuilder.RenameColumn(
                name: "status",
                table: "Payments",
                newName: "Status");

            migrationBuilder.RenameColumn(
                name: "provider",
                table: "Payments",
                newName: "Provider");

            migrationBuilder.RenameColumn(
                name: "currency",
                table: "Payments",
                newName: "Currency");

            migrationBuilder.RenameColumn(
                name: "amount",
                table: "Payments",
                newName: "Amount");

            migrationBuilder.RenameColumn(
                name: "id",
                table: "Payments",
                newName: "Id");

            migrationBuilder.RenameColumn(
                name: "user_id",
                table: "Payments",
                newName: "UserId");

            migrationBuilder.RenameColumn(
                name: "updated_at",
                table: "Payments",
                newName: "UpdatedAt");

            migrationBuilder.RenameColumn(
                name: "provider_receipt_url",
                table: "Payments",
                newName: "ProviderReceiptUrl");

            migrationBuilder.RenameColumn(
                name: "provider_payment_id",
                table: "Payments",
                newName: "ProviderPaymentId");

            migrationBuilder.RenameColumn(
                name: "failure_message",
                table: "Payments",
                newName: "FailureMessage");

            migrationBuilder.RenameColumn(
                name: "failure_code",
                table: "Payments",
                newName: "FailureCode");

            migrationBuilder.RenameColumn(
                name: "created_at",
                table: "Payments",
                newName: "CreatedAt");

            migrationBuilder.RenameColumn(
                name: "booking_id",
                table: "Payments",
                newName: "BookingId");

            migrationBuilder.RenameIndex(
                name: "IX_Payments_user_id",
                table: "Payments",
                newName: "IX_Payments_UserId");

            migrationBuilder.RenameIndex(
                name: "IX_Payments_provider_payment_id",
                table: "Payments",
                newName: "IX_Payments_ProviderPaymentId");

            migrationBuilder.RenameIndex(
                name: "IX_Payments_booking_id",
                table: "Payments",
                newName: "IX_Payments_BookingId");

            migrationBuilder.RenameColumn(
                name: "id",
                table: "Otps",
                newName: "Id");

            migrationBuilder.RenameColumn(
                name: "user_id",
                table: "Otps",
                newName: "UserId");

            migrationBuilder.RenameColumn(
                name: "otp_hash",
                table: "Otps",
                newName: "OtpHash");

            migrationBuilder.RenameIndex(
                name: "IX_Otps_user_id",
                table: "Otps",
                newName: "IX_Otps_UserId");

            migrationBuilder.RenameColumn(
                name: "type",
                table: "Notifications",
                newName: "Type");

            migrationBuilder.RenameColumn(
                name: "title",
                table: "Notifications",
                newName: "Title");

            migrationBuilder.RenameColumn(
                name: "message",
                table: "Notifications",
                newName: "Message");

            migrationBuilder.RenameColumn(
                name: "id",
                table: "Notifications",
                newName: "Id");

            migrationBuilder.RenameColumn(
                name: "user_id",
                table: "Notifications",
                newName: "UserId");

            migrationBuilder.RenameColumn(
                name: "is_read",
                table: "Notifications",
                newName: "IsRead");

            migrationBuilder.RenameIndex(
                name: "IX_Notifications_user_id",
                table: "Notifications",
                newName: "IX_Notifications_UserId");

            migrationBuilder.RenameColumn(
                name: "content",
                table: "Messages",
                newName: "Content");

            migrationBuilder.RenameColumn(
                name: "id",
                table: "Messages",
                newName: "Id");

            migrationBuilder.RenameColumn(
                name: "sender_id",
                table: "Messages",
                newName: "SenderId");

            migrationBuilder.RenameColumn(
                name: "receiver_id",
                table: "Messages",
                newName: "ReceiverId");

            migrationBuilder.RenameColumn(
                name: "is_read",
                table: "Messages",
                newName: "IsRead");

            migrationBuilder.RenameIndex(
                name: "IX_Messages_sender_id",
                table: "Messages",
                newName: "IX_Messages_SenderId");

            migrationBuilder.RenameIndex(
                name: "IX_Messages_receiver_id",
                table: "Messages",
                newName: "IX_Messages_ReceiverId");

            migrationBuilder.RenameColumn(
                name: "id",
                table: "Favorites",
                newName: "Id");

            migrationBuilder.RenameColumn(
                name: "car_id",
                table: "Favorites",
                newName: "CarId");

            migrationBuilder.RenameColumn(
                name: "user_id",
                table: "Favorites",
                newName: "UserId");

            migrationBuilder.RenameIndex(
                name: "IX_Favorites_car_id",
                table: "Favorites",
                newName: "IX_Favorites_CarId");

            migrationBuilder.RenameColumn(
                name: "reason",
                table: "CarUnavailableDates",
                newName: "Reason");

            migrationBuilder.RenameColumn(
                name: "id",
                table: "CarUnavailableDates",
                newName: "Id");

            migrationBuilder.RenameColumn(
                name: "start_date",
                table: "CarUnavailableDates",
                newName: "StartDate");

            migrationBuilder.RenameColumn(
                name: "end_date",
                table: "CarUnavailableDates",
                newName: "EndDate");

            migrationBuilder.RenameColumn(
                name: "car_id",
                table: "CarUnavailableDates",
                newName: "CarId");

            migrationBuilder.RenameIndex(
                name: "IX_CarUnavailableDates_car_id",
                table: "CarUnavailableDates",
                newName: "IX_CarUnavailableDates_CarId");

            migrationBuilder.RenameColumn(
                name: "year",
                table: "Cars",
                newName: "Year");

            migrationBuilder.RenameColumn(
                name: "transmission",
                table: "Cars",
                newName: "Transmission");

            migrationBuilder.RenameColumn(
                name: "status",
                table: "Cars",
                newName: "Status");

            migrationBuilder.RenameColumn(
                name: "model",
                table: "Cars",
                newName: "Model");

            migrationBuilder.RenameColumn(
                name: "features",
                table: "Cars",
                newName: "Features");

            migrationBuilder.RenameColumn(
                name: "description",
                table: "Cars",
                newName: "Description");

            migrationBuilder.RenameColumn(
                name: "color",
                table: "Cars",
                newName: "Color");

            migrationBuilder.RenameColumn(
                name: "brand",
                table: "Cars",
                newName: "Brand");

            migrationBuilder.RenameColumn(
                name: "id",
                table: "Cars",
                newName: "Id");

            migrationBuilder.RenameColumn(
                name: "updated_at",
                table: "Cars",
                newName: "UpdatedAt");

            migrationBuilder.RenameColumn(
                name: "price_per_day",
                table: "Cars",
                newName: "PricePerDay");

            migrationBuilder.RenameColumn(
                name: "owner_id",
                table: "Cars",
                newName: "OwnerId");

            migrationBuilder.RenameColumn(
                name: "location_city",
                table: "Cars",
                newName: "LocationCity");

            migrationBuilder.RenameColumn(
                name: "license_plate",
                table: "Cars",
                newName: "LicensePlate");

            migrationBuilder.RenameColumn(
                name: "created_at",
                table: "Cars",
                newName: "CreatedAt");

            migrationBuilder.RenameColumn(
                name: "car_license_image",
                table: "Cars",
                newName: "CarLicenseImage");

            migrationBuilder.RenameColumn(
                name: "average_rating",
                table: "Cars",
                newName: "AverageRating");

            migrationBuilder.RenameIndex(
                name: "IX_Cars_owner_id",
                table: "Cars",
                newName: "IX_Cars_OwnerId");

            migrationBuilder.RenameIndex(
                name: "IX_Cars_license_plate",
                table: "Cars",
                newName: "IX_Cars_LicensePlate");

            migrationBuilder.RenameColumn(
                name: "id",
                table: "CarImages",
                newName: "Id");

            migrationBuilder.RenameColumn(
                name: "image_path",
                table: "CarImages",
                newName: "ImagePath");

            migrationBuilder.RenameColumn(
                name: "car_id",
                table: "CarImages",
                newName: "CarId");

            migrationBuilder.RenameIndex(
                name: "IX_CarImages_car_id",
                table: "CarImages",
                newName: "IX_CarImages_CarId");

            migrationBuilder.RenameColumn(
                name: "status",
                table: "Bookings",
                newName: "Status");

            migrationBuilder.RenameColumn(
                name: "id",
                table: "Bookings",
                newName: "Id");

            migrationBuilder.RenameColumn(
                name: "updated_at",
                table: "Bookings",
                newName: "UpdatedAt");

            migrationBuilder.RenameColumn(
                name: "transaction_id",
                table: "Bookings",
                newName: "TransactionId");

            migrationBuilder.RenameColumn(
                name: "total_price",
                table: "Bookings",
                newName: "TotalPrice");

            migrationBuilder.RenameColumn(
                name: "start_date",
                table: "Bookings",
                newName: "StartDate");

            migrationBuilder.RenameColumn(
                name: "renter_id",
                table: "Bookings",
                newName: "RenterId");

            migrationBuilder.RenameColumn(
                name: "payment_confirmed_at",
                table: "Bookings",
                newName: "PaymentConfirmedAt");

            migrationBuilder.RenameColumn(
                name: "paid_amount",
                table: "Bookings",
                newName: "PaidAmount");

            migrationBuilder.RenameColumn(
                name: "end_date",
                table: "Bookings",
                newName: "EndDate");

            migrationBuilder.RenameColumn(
                name: "created_at",
                table: "Bookings",
                newName: "CreatedAt");

            migrationBuilder.RenameColumn(
                name: "car_id",
                table: "Bookings",
                newName: "CarId");

            migrationBuilder.RenameIndex(
                name: "IX_Bookings_renter_id",
                table: "Bookings",
                newName: "IX_Bookings_RenterId");

            migrationBuilder.RenameIndex(
                name: "IX_Bookings_car_id",
                table: "Bookings",
                newName: "IX_Bookings_CarId");

            migrationBuilder.CreateIndex(
                name: "IX_Users_Email",
                table: "Users",
                column: "Email",
                unique: true,
                filter: "[Email] IS NOT NULL");

            migrationBuilder.CreateIndex(
                name: "IX_Users_LicenseNumber",
                table: "Users",
                column: "LicenseNumber",
                unique: true,
                filter: "[LicenseNumber] IS NOT NULL");

            migrationBuilder.CreateIndex(
                name: "IX_Users_Phone",
                table: "Users",
                column: "Phone",
                unique: true,
                filter: "[Phone] IS NOT NULL");

            migrationBuilder.CreateIndex(
                name: "IX_Bookings_TransactionId",
                table: "Bookings",
                column: "TransactionId",
                unique: true,
                filter: "[TransactionId] IS NOT NULL");

            migrationBuilder.AddForeignKey(
                name: "FK_Bookings_Cars_CarId",
                table: "Bookings",
                column: "CarId",
                principalTable: "Cars",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Bookings_Users_RenterId",
                table: "Bookings",
                column: "RenterId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_CarImages_Cars_CarId",
                table: "CarImages",
                column: "CarId",
                principalTable: "Cars",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Cars_Users_OwnerId",
                table: "Cars",
                column: "OwnerId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_CarUnavailableDates_Cars_CarId",
                table: "CarUnavailableDates",
                column: "CarId",
                principalTable: "Cars",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Favorites_Cars_CarId",
                table: "Favorites",
                column: "CarId",
                principalTable: "Cars",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Favorites_Users_UserId",
                table: "Favorites",
                column: "UserId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Messages_Users_ReceiverId",
                table: "Messages",
                column: "ReceiverId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Messages_Users_SenderId",
                table: "Messages",
                column: "SenderId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Notifications_Users_UserId",
                table: "Notifications",
                column: "UserId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Otps_Users_UserId",
                table: "Otps",
                column: "UserId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Payments_Bookings_BookingId",
                table: "Payments",
                column: "BookingId",
                principalTable: "Bookings",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_Payments_Users_UserId",
                table: "Payments",
                column: "UserId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.SetNull);

            migrationBuilder.AddForeignKey(
                name: "FK_Reviews_Cars_CarId",
                table: "Reviews",
                column: "CarId",
                principalTable: "Cars",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            migrationBuilder.AddForeignKey(
                name: "FK_Reviews_Users_RenterId",
                table: "Reviews",
                column: "RenterId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);
        }
    }
}
