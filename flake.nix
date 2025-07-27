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
        ./nixos/hardware-configuration.nix
        ./nixos/system.nix
        ./nixos/services.nix
        ./nixos/packages.nix
        ./nixos/configuration.nix

        home-manager.nixosModules.home-manager {
          home-manager.useGlobalPkgs = true;
          home-manager.useUserPackages = true;
          # --- ADDED: Tell Home Manager to back up conflicting files ---
          home-manager.backupFileExtension = "backup";
          home-manager.users.balint = import ./nixos/home.nix;
        }
      ];
    };
  };
}

