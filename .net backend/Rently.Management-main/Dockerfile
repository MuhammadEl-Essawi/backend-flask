# ──────────────────────────────────────────────────────
# ⚡ Rently .NET Management API – Multi-stage Dockerfile
# ──────────────────────────────────────────────────────

# ── Stage 1: Build ──
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copy project file and restore dependencies (cached layer)
COPY Rently.Management.csproj ./
RUN dotnet restore Rently.Management.csproj

# Copy everything else and publish
COPY . .
RUN dotnet publish Rently.Management.csproj -c Release -o /app/publish --no-restore

# ── Stage 2: Runtime ──
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app

COPY --from=build /app/publish .

ENV ASPNETCORE_URLS=http://+:5001 \
    ASPNETCORE_ENVIRONMENT=Development \
    DOTNET_RUNNING_IN_CONTAINER=true

EXPOSE 5001

ENTRYPOINT ["dotnet", "Rently.Management.dll"]
