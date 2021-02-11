{
  description = "ExAO DAP";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.poetry2nix-src.url = "github:nix-community/poetry2nix";

  outputs = { self, nixpkgs, poetry2nix-src }: 
    let
        pkgs = import nixpkgs { system = "x86_64-linux"; overlays = [ poetry2nix-src.overlay ]; };
    in
    let
      dapEnv = pkgs.poetry2nix.mkPoetryEnv {
        projectDir = ./.;
        editablePackageSources = {
          exao_dap = ./exao_dap;
        };
      };
    in
    {
    defaultPackage.x86_64-linux = dapEnv;
    nixosModules.dap = let
      checkoutKeyPath = /root/.ssh/id_ed25519_dap;
      checkoutPath = /home/dap/exao_dap;
    in
    {
      users.extraUsers.dap = {
        isNormalUser = false;
        createHome = true;
        home = "/home/dap";
        description = "Data Analysis Platform";
      };
      systemd.services.ensure_checkout_key = {
        wantedBy = [ "multi-user.target" ];
        script = ''
          if [[ ! -e ${checkoutKeyPath} ]]; then 
            ssh-keygen -t ed25519 -C "dap@xwcl.science" -f ${checkoutKeyPath} -N ""
          fi
        '';
        serviceConfig = {
          User = "root";
          RemainAfterExit = true;
        };
      };
      systemd.services.updatedap = {
        after = [ "ensure_checkout_key.service" ];
        wantedBy = [ "multi-user.target" ];
        script = ''
          export GIT_SSH_COMMAND='${pkgs.openssh}/bin/ssh -i ${checkoutKeyPath}
          if [[ ! -e ${checkoutPath} ]]; then
            ${pkgs.git}/bin/git clone git@github.com:xwcl/exao_dap.git ${checkoutPath}
          fi
          cd ${checkoutPath}
          ${pkgs.git}/bin/git pull
          chown -R dap /home/dap
          mkdir -p /var/lib/dap
          chown -R dap /var/lib/dap
        '';
        serviceConfig = {
          User = "root";
          RemainAfterExit = true;
        };
      };
      systemd.services.dap = {
        after = [ "updatedap.service" ];
        wantedBy = [ "multi-user.target" ];
        environment = {};
        script = ''
        cd ${checkoutPath}
        ${dapEnv}/bin/gunicorn exao_dap.wsgi
        '';
        serviceConfig = {
          User = "dap";
        };
      };
    };
  };
}
