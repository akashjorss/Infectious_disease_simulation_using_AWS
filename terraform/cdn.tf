resource "aws_s3_bucket" "fe_s3" {
  bucket = "cc-project-2020-fe"
  acl    = "private"

  tags = {
    Name = "FE code"
  }

  lifecycle {
    prevent_destroy = true
  }
}

locals {
  s3_origin_id = "cc-project-frontend"
}

resource "aws_cloudfront_origin_access_identity" "fe" {
  comment = "To Access FE Codebase only via cloudfront"
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions = [
    "s3:GetObject"]
    resources = [
    "${aws_s3_bucket.fe_s3.arn}/*"]

    principals {
      type = "AWS"
      identifiers = [
      aws_cloudfront_origin_access_identity.fe.iam_arn]
    }
  }

  statement {
    actions = [
    "s3:ListBucket"]
    resources = [
    aws_s3_bucket.fe_s3.arn]

    principals {
      type = "AWS"
      identifiers = [
      aws_cloudfront_origin_access_identity.fe.iam_arn]
    }
  }
}

resource "aws_s3_bucket_policy" "cdn_s3_policy" {
  bucket = aws_s3_bucket.fe_s3.id
  policy = data.aws_iam_policy_document.s3_policy.json
}


resource "aws_cloudfront_distribution" "fe_s3_distribution" {
  origin {
    domain_name = aws_s3_bucket.fe_s3.bucket_regional_domain_name
    origin_id   = local.s3_origin_id
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.fe.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CDN for CC project"
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods = [
      "DELETE",
      "GET",
      "HEAD",
      "OPTIONS",
      "PATCH",
      "POST",
    "PUT"]
    cached_methods = [
      "GET",
    "HEAD"]
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  price_class = "PriceClass_200"

  //  restrictions {
  //    geo_restriction {
  //      restriction_type = "whitelist"
  //      locations = [
  //        "US",
  //        "CA",
  //        "GB",
  //        "DE"]
  //    }
  //  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Environment = "test"
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  //  Costly to create hence prevent destroy

  lifecycle {
    prevent_destroy = true
  }
}