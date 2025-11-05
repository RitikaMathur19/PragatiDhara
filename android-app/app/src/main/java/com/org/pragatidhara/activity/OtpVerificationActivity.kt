package com.org.pragatidhara.activity

import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.widget.ArrayAdapter
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

        // populate country code spinner
        val countryCodes = listOf("+91", "+1", "+44")
        binding.spinnerCountryCode.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, countryCodes)

        // initial button/visibility states
        binding.btnSendOtp.isEnabled = true
        binding.btnVerifyOtp.isEnabled = false
        binding.etOtp.visibility = View.GONE
        binding.btnVerifyOtp.visibility = View.GONE
        binding.tvResendOtp.visibility = View.GONE

        // Enable Verify button only when OTP length == 6
        binding.etOtp.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                binding.btnVerifyOtp.isEnabled = s?.length == 6
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        binding.btnSendOtp.setOnClickListener {
            val countryCode = binding.spinnerCountryCode.selectedItem.toString()
            val mobileRaw = binding.etMobileNumber.text.toString()
            val mobileDigits = mobileRaw.filter { it.isDigit() }

            if (mobileDigits.length != 10) {
                Toast.makeText(this, "Please enter a valid 10-digit mobile number", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Mock API call to send OTP
            binding.btnSendOtp.isEnabled = false // allow only first send; resend will re-enable
            Toast.makeText(this, "OTP sent to $countryCode $mobileDigits", Toast.LENGTH_SHORT).show()

            // Reveal OTP UI elements for verification
            binding.etOtp.visibility = View.VISIBLE
            binding.btnVerifyOtp.visibility = View.VISIBLE
            binding.tvResendOtp.visibility = View.VISIBLE
            binding.etOtp.requestFocus()
        }

        binding.btnVerifyOtp.setOnClickListener {
            val otp = binding.etOtp.text.toString()
            if (otp == "123456") { // Mock OTP verification
                val intent = Intent(this, VehicleDetailsActivity::class.java)
                intent.putExtra("fullName", fullName)
                intent.putExtra("mobileNumber", binding.etMobileNumber.text.toString())
                startActivity(intent)
            } else {
                Toast.makeText(this, "Invalid OTP", Toast.LENGTH_SHORT).show()
            }
        }

        binding.tvResendOtp.setOnClickListener {
            // Allow user to request resend which re-enables the Send button
            binding.btnSendOtp.isEnabled = true
            Toast.makeText(this, "OTP resent (you can send again)", Toast.LENGTH_SHORT).show()
        }
    }
}