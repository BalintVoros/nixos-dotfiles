{
  description = "Balint's NixOS Flake";

  # --- Inputs ---
  # Here we define where all our software comes from.
  # We are "pinning" them to a specific version for reproducibility.
  inputs = {
    # NixOS packages. We'll use the stable 24.05 release.
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";

    # Home Manager, using the version that matches our NixOS release.
    home-manager.url = "github:nix-community/home-manager/release-24.05";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  # --- Outputs ---
  # This function takes our inputs and builds our system configuration.
  outputs = { self, nixpkgs, home-manager, ... }: {
    # This is your main NixOS configuration. We name it 'nixos' to match your hostname.
    nixosConfigurations.nixos = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = { }; # For advanced use later
      modules = [
        # Import your existing configuration.nix
        ./nixos/configuration.nix

        # Import the Home Manager module to configure your user
        home-manager.nixosModules.home-manager {
          home-manager.useGlobalPkgs = true;
          home-manager.useUserPackages = true;
          # Tell Home Manager to build the config for 'balint' using your home.nix
          home-manager.users.balint = import ./nixos/home.nix;
        }
      ];
    };
  };
}

