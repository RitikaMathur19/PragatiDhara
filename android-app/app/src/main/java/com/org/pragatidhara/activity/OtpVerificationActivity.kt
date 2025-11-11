package com.org.pragatidhara.activity

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.org.pragatidhara.databinding.ActivityOtpVerificationBinding

class OtpVerificationActivity : AppCompatActivity() {

    private lateinit var binding: ActivityOtpVerificationBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityOtpVerificationBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val fullName = intent.getStringExtra("fullName")

        binding.btnSendOtpCard.setOnClickListener {
            val mobileNumber = binding.etMobileNumberBottom.text.toString()
            if (mobileNumber.isNotEmpty()) {
                // Mock API call to send OTP
                Toast.makeText(this, "OTP sent to $mobileNumber", Toast.LENGTH_SHORT).show()
            }
        }

        binding.btnSendOtpCard.setOnClickListener {
            // In a real app, you would verify the OTP here
            val otp = getOtpFromFields()
            if (otp == "123456") { // Mock OTP verification
                val intent = Intent(this, VehicleDetailsActivity::class.java)
                intent.putExtra("fullName", fullName)
                intent.putExtra("mobileNumber", binding.etMobileNumberBottom.text.toString())
                startActivity(intent)
            } else {
                Toast.makeText(this, "Invalid OTP", Toast.LENGTH_SHORT).show()
            }
        }

        binding.tvResendOtpCard.setOnClickListener {
            // Mock API call to resend OTP
            Toast.makeText(this, "OTP resent", Toast.LENGTH_SHORT).show()
        }
    }

    private fun getOtpFromFields(): String {
        return "" + binding.etOtp1.text.toString() + "" +
                binding.etOtp2.text.toString() + "" +
                binding.etOtp3.text.toString() + "" +
                binding.etOtp4.text.toString() + "" +
                binding.etOtp5.text.toString() + "" +
                binding.etOtp6.text.toString()
    }
}