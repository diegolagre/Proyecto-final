terraform {
  # La configuración se inyecta durante terraform init para no guardar nombres
  # de cuenta, credenciales ni valores específicos del ambiente en Git.
  backend "s3" {}
}
