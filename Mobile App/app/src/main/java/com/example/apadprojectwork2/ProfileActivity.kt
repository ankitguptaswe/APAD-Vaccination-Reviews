package com.example.apadprojectwork2

import android.app.ProgressDialog
import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.view.View
import androidx.appcompat.app.ActionBar
import com.example.apadprojectwork2.LoginActivity
import com.example.apadprojectwork2.databinding.ActivityProfileBinding
import com.example.apadprojectwork2.databinding.ActivitySignUpBinding
import com.google.firebase.auth.FirebaseAuth
import kotlinx.android.synthetic.main.theme_row.*

class ProfileActivity : AppCompatActivity() {

    private lateinit var binding: ActivityProfileBinding
    private  lateinit var actionBar: ActionBar
    private lateinit var progressDialog: ProgressDialog
    private lateinit var firebaseAuth: FirebaseAuth

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityProfileBinding.inflate(layoutInflater)
        setContentView(binding.root)
        actionBar = supportActionBar!!
        actionBar.title = "Profile"

        firebaseAuth = FirebaseAuth.getInstance()
        checkUser()

        //handle logout
        binding.logoutBtn.setOnClickListener{
            firebaseAuth.signOut()
            checkUser()
        }

        binding.buttonReview.setOnClickListener{
            onCreateReviewClick()
        }
    }

    override fun onResume() {
        super.onResume()
        binding = ActivityProfileBinding.inflate(layoutInflater)
        setContentView(binding.root)
        actionBar = supportActionBar!!
        actionBar.title = "Profile"

        firebaseAuth = FirebaseAuth.getInstance()
        checkUser()

        //handle logout
        binding.logoutBtn.setOnClickListener{
            firebaseAuth.signOut()
            checkUser()
        }

        binding.buttonReview.setOnClickListener{
            onCreateReviewClick()
        }
    }

    fun onViewThemesClick(view: View) {
        val intent = Intent(this@ProfileActivity, ThemeActivity::class.java)
        startActivity(intent)
    }

    fun onCreateReviewClick() {
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
    }

    private fun checkUser() {
        val firebaseUser = firebaseAuth.currentUser
        if (firebaseUser!= null) {
            val email = firebaseUser.email
            binding.emailTv.text = email
        } else {
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
        }
    }
}