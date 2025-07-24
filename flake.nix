{
  description = "Balint's NixOS Flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    home-manager.url = "github:nix-community/home-manager/release-24.05";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, home-manager, ... }: {
    nixosConfigurations.nixos = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = { };
      modules = [
        # Import all the system modules directly here
        ./nixos/hardware-configuration.nix
        ./nixos/system.nix
        ./nixos/services.nix
        ./nixos/packages.nix

        # Import the main configuration.nix for the flakes setting
        ./nixos/configuration.nix

        # Import the Home Manager module
        home-manager.nixosModules.home-manager {
          home-manager.useGlobalPkgs = true;
          home-manager.useUserPackages = true;
          home-manager.users.balint = import ./nixos/home.nix;
        }
      ];
    };
  };
}

